# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: performance_logger.py
#
# description
"""\n\n
    take logfile as input and report performance of full / single optimizations
"""

import sys
import re
import os.path
from datetime import datetime
from argparse import ArgumentParser
from glob import glob

VERSION = '0.1'

def get_job(line):
    hit = re.search(r'MSG DEF_APSCommandSetServerState______ Warning mbjob00004.*\D(\d+)$', line)
    if hit:
        return int(hit.group(1))
    hit = re.search(r"(job number=|job no=|jobnr\:\s+)(\d+)", line)
    if hit:
        return int(hit.group(2))
    return None

def get_datetime(line):
    hit = re.search(r"^(\d{2}.\d{2}.\d{4}\s+\d{2}\:\d{2}\:\d{2})", line)
    if hit:
        return datetime.strptime(hit.group(1), '%d.%m.%Y %H:%M:%S')
    return None

class PerformanceTrace:
    """one job item"""
    def __init__(self, start_line, frontlines=None):
        self._lines = []
        if frontlines is not None:
            self._lines.extend(frontlines)
        self._lines.append(start_line)
        self._job = None
        for line in self._lines:
            self.check_for_job(line)

    def line_count(self):
        return len(self._lines)

    def add(self, line):
        self._lines.append(line)
        if self._job is None:
            self.check_for_job(line)

    def check_for_job(self, line):
        job = get_job(line)
        if job is not None:
            self._job = job

    def get_type(self):
        for line in self._lines:
            if line.find('calcCtp')!=-1 or line.find('CTP')!=-1:
                return 'ctp'
            if line.find('calcAll')!=-1:
                return 'opti'
            if line.find('sync only')!=-1 or \
               line.find('begin syncronize')!=-1 or \
               line.find('Optimization finished sync done')!=-1:
                return 'sync'
        return 'unknown'

    def get_proc_act_info(self):
        for line in self._lines:
            hit = re.search(r'APS Scheduler  (#proc: \d+, #act: \d+)', line)
            if hit:
                return hit.group(1)
        return None

    def get_mid1(self):
        for line in self._lines:
            if line.find('buildObjectModel')!=-1:
                return get_datetime(line)
        return None

    def get_mid2(self):
        for line in self._lines:
            if line.find('Sent')!=-1:
                return get_datetime(line)
        return None

    def get_start_timepoint(self):
        """get start timepoint of job"""
        return get_datetime(self._lines[0])

    def find_result_received(self):
        """get line indox with 'DEF_APSCommandSetServerState______ ResultReceived', None otherwise"""
        for idx in range(-1, -len(self._lines), -1):
            if self._lines[idx].find('ResultReceived') != -1:
                return idx
        return None

    def get_last_line_idx(self):
        """get line index of last line, maybe skip queue cancel line"""
        idx = self.find_result_received()
        if idx:
            return idx
        idx = -1
        if self._lines[-1].find('checkForCancelCommandQueue') != -1 and len(self._lines) > 1:
            idx = -2
        return idx

    def get_mem_min(self):
        return self.get_mem(True)
    def get_mem_max(self):
        return self.get_mem(False)

    def get_mem(self, get_min):
        mem_tmp = None
        for line in self._lines:
            # peak memory [gb]: 0.37
            hit = re.search(r'peak memory \[gb\]:\s+([0-9\.]+)', line)
            if hit:
                val = float(hit.group(1))
                if mem_tmp is None: 
                    mem_tmp = val
                elif get_min and val < mem_tmp:
                    mem_tmp = val
                elif not get_min and val > mem_tmp:
                    mem_tmp = val
        if mem_tmp is None:
            mem_tmp = -1.0 if get_min else 9999.0
        return mem_tmp

    def start_to_end(self):
        start = get_datetime(self._lines[0])
        mid1 = self.get_mid1()
        mid2 = self.get_mid2()
        end = get_datetime(self._lines[self.get_last_line_idx()])
        if mid1 is None:
            mid1 = start
        if mid2 is None:
            mid2 = end
        startup = (mid1 - start).total_seconds()
        mid = (mid2 - mid1).total_seconds()
        listener = (end - mid2).total_seconds()
        return (int(startup), int(mid), int(listener))

    def strip_to_key(self, line):
        if line.find('updateProcessStructures') != -1:
            return 'updateProcessStructures'
        pos = line.find('|')
        if pos != -1:
            return line[pos:]
        return line

    def compress(self):
        start_idx = 0
        key = None
        cluster = []
        for idx, line in enumerate(self._lines):
            short_line = self.strip_to_key(line)
            if short_line == key:
                continue
            if idx - start_idx > 5:
                cluster.append((start_idx, idx-1))
            start_idx = idx
            key = short_line
        cluster.reverse()
        for idx_start, idx_end in cluster:
            self._lines[idx_start + 1] = "... %dx\n" % (idx_end - idx_start + 1)
            del self._lines[idx_start + 2 : idx_end]
        
    def elapsed_total(self):
        start = get_datetime(self._lines[0])
        end = get_datetime(self._lines[self.get_last_line_idx()])
        diff = end - start
        return diff.total_seconds()

    def job(self):
        return self._job

    def __str__(self):
        self.compress()
        return ''.join(self._lines)

def have_change_job_line(logfile, code):
    for line in open(logfile, encoding=code):
        if re.search(r"^.*Change job number", line):
            return True
    return False

def show_report(performance_items, stream=sys.stdout):
    time2item = {}
    for item in performance_items:
        secs = int(item.elapsed_total())
        time2item.setdefault(secs, [])
        time2item[secs].append(item)

    stream.write('#total: %d\n' % len(performance_items))
    if len(time2item) > 0:
        stream.write("\tseconds: #items\n")
    for secs in sorted(time2item):
        stream.write("\t%4d: %4d\n" % (secs, len(time2item[secs])))
    print()

    for idx, item in enumerate(performance_items):
        line = re.sub(r'[^\x00-\x7F]', '', str(item)) # strip non ascii characters
        stream.write("%02d %s: %s %s %s\n%s\n" % (idx, item.get_type(), item.elapsed_total(),
                                                  item.start_to_end(), item.get_start_timepoint(), line))

def show_short_report(performance_items, stream=sys.stdout):
    stream.write("Index;Startzeit;Dauer;Was;#proc #acts;Speicher_min;Speicher_max\n")
    for idx, item in enumerate(performance_items):
        line = "%02d;%s;%s;%s;%s;%0.1f;%0.1f" % (idx, item.get_start_timepoint(), item.elapsed_total(), item.get_type(),
                                        item.get_proc_act_info(), item.get_mem_min(), item.get_mem_max())
        line = line.replace('.', ',')
        stream.write(line + "\n")
        
        """
        stream.write("%02d %s: %s %s %s %0.2f %0.2f %s\n" % (idx, item.get_type(), item.elapsed_total(),
                                             item.start_to_end(), item.get_start_timepoint(), 
                                             item.get_mem_min(), item.get_mem_max(),
                                             item.get_proc_act_info()))
        """

def test_encoding(message_file):
    """check for file encoding"""
    encodings = ["UTF-8", "ISO-8859-1", "latin-1"]

    if not os.path.exists(message_file):
        raise FileNotFoundError(message_file)

    for item in encodings:
        try:
            for _ in open(message_file, encoding=item):
                pass
            return item
        except UnicodeDecodeError:
            pass

    raise "Cannot get right encoding, tried %s" % str(encodings)

def performance_report(logfile, mode_52):
    """logfile and grep performance of single / full optimization"""
    code = test_encoding(logfile)

    rgx_start = re.compile(r"^.*Change job number")
    if not have_change_job_line(logfile, code):
        rgx_start = re.compile(r"^.*SERVER_STATE\: Receiving Ground Data")

    if mode_52:
        rgx_start = re.compile(r"receive Order!")

    mid_expressions = [r"SERVER_STATE",
                       r'buildObjectModel Modelltyp',
                       r'-- calcAll --',
                       r'begin calcCtp',
                       r'begin syncronize, job no',
                       r'Decomposition\s+\|',
                       r'ApsModelerIlo\:\:createIlogModel',
                       r'ApsSchedulerCPO_optimalDemandTimes',
                       r'Sen[dt].*Solution to ERP',
                       r'DEF_APSCommandSetServerState______',
                       r'end syncronize',
                       r'tardinessReasoning',
                       r'ApsSchedulerCPO_emptySchedule',
                       r'elapsed milliseconds since last job start',
                       r'APS Scheduler\s+#proc',
                       r'invoke restart service'
                       ]
    rgx_mid = re.compile(r"^.*(%s)" % '|'.join(mid_expressions))

    rgx_end = re.compile(r'.*Send CTP\-Prod Solution to ERP.*')

    rgx_all = [rgx_start, rgx_mid]

    performance_items = []
    job_to_item = {}
    job_to_lines = {}
    last_job_no = None

    perf_item = None
    for line in open(logfile, encoding=code):
        # skip nul nul nul lines
        if len(line) > 0 and line[0] == '\0':
            continue

        for rgx in rgx_all:
            hit = rgx.search(line)
            if hit:
                job_no = get_job(line)

                # in 5.2 we have no real start rgx and need to detect end of job
                if mode_52 and rgx_end.search(line):
                    if perf_item is None:
                        perf_item = PerformanceTrace(line)
                    else:
                        perf_item.add(line)
                    performance_items.append(perf_item)
                    perf_item = None
                    break

                if perf_item is None:
                    perf_item = PerformanceTrace(line)

                elif rgx == rgx_start:
                    if perf_item is not None:
                        if perf_item.line_count()==1 and mode_52:
                            perf_item.add(line)
                        elif job_no is not None and job_no == perf_item.job():
                            perf_item.add(line)
                        else:
                            performance_items.append(perf_item)
                            job_to_item[perf_item.job()] = perf_item
                            if not job_no and last_job_no:
                                job_no = last_job_no
                            if job_no and job_no in job_to_lines:
                                perf_item = PerformanceTrace(line, job_to_lines[job_no])
                                del job_to_lines[job_no]
                            else:
                                perf_item = PerformanceTrace(line)
                else:
                    if job_no is None:
                        perf_item.add(line)
                    else:
                        if perf_item.job() == job_no:
                            perf_item.add(line)
                        elif job_no in job_to_item:
                            job_to_item[job_no].add(line)
                        else:
                            job_to_lines.setdefault(job_no, [])
                            job_to_lines[job_no].append(line)
                            last_job_no = job_no
                break

    if perf_item is not None:
        performance_items.append(perf_item)

    return performance_items

def get_duration(tp1, tp2):
    h1, m1, s1 = [int(x) for x in re.search(r'(\d{2}):(\d{2}):(\d{2})', tp1).groups()]
    h2, m2, s2 = [int(x) for x in re.search(r'(\d{2}):(\d{2}):(\d{2})', tp2).groups()]
    return h2 * 60 * 60 + m2 * 60 + s2 - (h1 * 60 * 60 + m1 * 60 + s1)

def queue_log_report(filename, stream=sys.stdout):
    rgx = re.compile(r'(\d{2}\.\d{2}\.\d{4})\s+(\d{2}:\d{2}:\d{2})\s+(\S+).*#(\d+).*(p_.*\.p).*(beendet|beginnt)')
    prev_tp = prev_job_id = prev_dt =None
    for line in open(filename):
        hit = rgx.search(line)
        if hit:
            print("hit")
            dt, tp, who, job_id, prg, _ = hit.groups()
            if prev_dt != dt:
                stream.write("\n\n%s" % dt)
                print("\n\n%s" % dt)
                prev_dt = dt
            if prev_job_id == job_id:
                duration = get_duration(prev_tp, tp)
                stream.write("job %s  duration=%02d start=%s end=%s (%s) %s" % (job_id, duration, prev_tp, tp, prg, who))
            prev_tp = tp
            prev_job_id = job_id

def batch_run(dirname, mode_52):
    """for each logfile within dirname do performance report"""
    logfiles = glob(dirname + "/*.log")
    for logfile in logfiles:
        report_data = performance_report(logfile, mode_52)
        dirname = os.path.dirname(logfile)
        name = os.path.basename(logfile)

        name = name.replace('opt-production-APS1', 'jobs')
        name = name.replace('.log', '.txt')
        out = os.path.join(dirname, name)
        stream = open(out, 'w')
        show_report(report_data, stream)
        stream.close()

def concat_logs(dirname):
    logfiles = glob(dirname + "/*.log")
    logfiles.sort()
    # check for special logfile without timestamp
    if not re.search(r'_\d+\d+\.log$', logfiles[0]):
        logfiles.append(logfiles.pop(0))
    result = os.path.join(dirname, "summary._tmp_")
    with open(result, 'w') as outfile:
        for fname in logfiles:
            with open(fname) as infile:
                for line in infile:
                    outfile.write(line)
    return result

def parse_arguments():
    """parse arguments from command line"""
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)

    parser.add_argument('logfile', metavar='logfile', help='input logfile')
    parser.add_argument('--queue_log', action="store_true", # or store_false
                        dest="queue_log", default=False, # negative store value
                        help="parse queue log and print contained job info to console")
    parser.add_argument('--mode_52', action="store_true", # or store_false
                        dest="mode_52", default=False, # negative store value
                        help="parse logfile with 5.2 mode")
    parser.add_argument('-b', '--batch', action='store_true',
                        dest='batch_run', default=False)
    parser.add_argument('-c', '--concat', action='store_true',
                        dest='concat_run', default=False)
    return parser.parse_args()

def main():
    """main function"""
    args = parse_arguments()
    filename = args.logfile

    if args.queue_log:
        queue_log_report(filename)
        return 0

    if args.batch_run:
        batch_run(filename, args.mode_52)
        return 0

    if args.concat_run:
        try:
            concatinated_log = concat_logs(filename)
            report_data = performance_report(concatinated_log, args.mode_52)
            with open(os.path.join(filename, "summary.txt"), 'w') as outfile:
                show_report(report_data, outfile)
            #with open(os.path.join(filename, "summary_short.csv"), 'w') as outfile:
            #    show_short_report(report_data, outfile)
        finally:
            if os.path.exists(concatinated_log):
                #os.remove(concatinated_log)
                pass
        return 0

    report_data = performance_report(filename, args.mode_52)
    show_report(report_data)
    return 0

if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
