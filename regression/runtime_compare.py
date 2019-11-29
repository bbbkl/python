# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: runtime_compare.py
#
# description
"""\n\n
    recursevly watch out for result.log / reference.log pairs.
    compare each with respect to runtime. sync / complete optimization is compared directly, CTPs are compared in bulk
    write runtime_compare.csv output.
"""

import sys
import re
import os.path
import csv
from datetime import datetime
from argparse import ArgumentParser
from glob import glob

VERSION = '0.1'

def get_job(line):
    hit = re.search('MSG DEF_APSCommandSetServerState______ Warning mbjob00004.*\D(\d+)$', line)
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
    
    def start_to_end(self):
        start = get_datetime(self._lines[0])
        mid1 = self.get_mid1()
        mid2 = self.get_mid2()
        end = get_datetime(self._lines[-1])
        if mid1 is None: mid1 = start
        if mid2 is None: mid2 = end
        startup = (mid1 - start).total_seconds()
        mid = (mid2 - mid1).total_seconds()
        listener = (end - mid2).total_seconds()
        return (int(startup), int(mid), int(listener))
    
    def elapsed_total(self):
        start = get_datetime(self._lines[0])
        end = get_datetime(self._lines[-1])
        diff = end - start
        return diff.total_seconds()
            
    def job(self):
        return self._job
        
    def __str__(self):
        return ''.join(self._lines)

def have_change_job_line(logfile, code):
    for line in open(logfile, encoding=code):
        if re.search(r"^.*Change job number", line):
            return True
    return False 

def show_report(performance_items, stream=sys.stdout):
    timeToItem = {}
    for item in performance_items:
        secs = int(item.elapsed_total())
        timeToItem.setdefault(secs, [])
        timeToItem[secs].append(item)
    
    stream.write('#total: %d\n' % len(performance_items))
    if len(timeToItem) > 0:
        stream.write("\tseconds: #items\n")
    for secs in sorted(timeToItem):
        stream.write("\t%4d: %4d\n" % (secs, len(timeToItem[secs]))) 
    print()
    
    for idx, item in enumerate(performance_items):  
        line = re.sub(r'[^\x00-\x7F]', '', str(item)) # strip non ascii characters
        stream.write("%02d %s: %s %s\n%s\n" % (idx, item.get_type(), item.elapsed_total(), item.start_to_end(), line))

def test_encoding(message_file):
    """check for file encoding"""
    encodings = ["UTF-8", "ISO-8859-1", "latin-1"]
    
    if not os.path.exists(message_file):
        raise FileNotFoundError(message_file)
    
    for item in encodings:
        try:
            for line in open(message_file, encoding=item):
                pass
            return item
        except:
            pass
        
    raise ("Cannot get right encoding, tried %s" % str(encodings))

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
                       r'Sen[dt].*Solution to ERP',
                       r'DEF_APSCommandSetServerState______',
                       r'end syncronize',
                       r'elapsed milliseconds since last job start',
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
  
def read_times(logfile):
    times = {}    
    times.setdefault('ctp', [])
    times.setdefault('opt', "")
    times.setdefault('sync', "")

    with open(logfile, "rb") as f:
        first = f.readline() 

        f.seek(-2, os.SEEK_END)        
        last = f.readline()
        i = 2

        while get_datetime(last.decode()) is None:            
            f.seek(-2 * i, os.SEEK_END)
            i = i + 1
            last = f.readline()
        times['total'] = (get_datetime(last.decode()) - get_datetime(first.decode())).total_seconds()

    report_data = performance_report(logfile, False) # mode_52 = yes / no 
    for (perf_item) in report_data:
        if perf_item.get_type() == 'opti':
            times['opt'] = perf_item.elapsed_total()
        elif perf_item.get_type() == 'sync':
            times['sync'] = perf_item.elapsed_total()
        elif perf_item.get_type() == 'ctp':
            times['ctp'].append(perf_item.elapsed_total())
        else:
            print("type: " + perf_item.get_type() + ", job: " + str(perf_item.job()) + ", duration: " + str(perf_item.elapsed_total()))
    
    return times

def compare_logfiles(fn_ref, fn_res):
    """compare given file pair"""
    print(fn_ref + ", " + fn_res + "\n")
    ref_times = read_times(fn_ref)
    n_ctp = 0    

    ref_max_ctp = 0
    ref_min_ctp = 9999999999
    ref_sum_ctp = 0
    for (time) in ref_times['ctp']:
        ref_sum_ctp += time
        ref_max_ctp = max(ref_max_ctp, time)
        ref_min_ctp = min(ref_min_ctp, time)
        n_ctp += 1
    if n_ctp > 0:
        ref_avg_ctp = ref_sum_ctp / n_ctp
    else:
        ref_avg_ctp = ""

    res_times = read_times(fn_res)
    res_max_ctp = 0
    res_min_ctp = 9999999999
    res_sum_ctp = 0
    for (time) in res_times['ctp']:
        res_sum_ctp += time
        res_max_ctp = max(res_max_ctp, time)
        res_min_ctp = min(res_min_ctp, time)      
    if n_ctp > 0:
        res_avg_ctp = res_sum_ctp / n_ctp
    else:
        res_avg_ctp = ""  
    
    line = {}
    #line.setdefault('opt_ref', "")
    #line.setdefault('opt_res', "")
    #line.setdefault('sync_ref', "")
    #line.setdefault('sync_res', "")

    line['total_ref'] = ref_times['total']
    line['total_res'] = res_times['total']
    line['opt_ref'] =  ref_times['opt']    
    line['opt_res'] =  res_times['opt']    
    line['sync_ref'] =  ref_times['sync']    
    line['sync_res'] =  res_times['sync']    
    line['sum_ctp_ref'] = ref_sum_ctp
    line['sum_ctp_res'] = res_sum_ctp
    line['avg_ctp_ref'] = ref_avg_ctp
    line['avg_ctp_res'] = res_avg_ctp
    line['min_ctp_ref'] = ref_min_ctp
    line['min_ctp_res'] = res_min_ctp    
    line['max_ctp_ref'] = ref_max_ctp
    line['max_ctp_res'] = res_max_ctp 
    line['n_ctp'] = n_ctp
    line['remainder_ref'] = ref_times['total'] - ref_sum_ctp
    if not type(ref_times['opt']) is str:
        line['remainder_ref'] -= ref_times['opt']
    if not type(ref_times['sync']) is str:
        line['remainder_ref'] -= ref_times['sync']
    line['remainder_res'] = res_times['total'] - res_sum_ctp
    if not type(res_times['opt']) is str:
        line['remainder_res'] -= res_times['opt']
    if not type(res_times['sync']) is str:
        line['remainder_res'] -= res_times['sync']
    if n_ctp == 0:
        line['sum_ctp_ref'] = ""
        line['sum_ctp_res'] = ""
        line['avg_ctp_ref'] = ""
        line['avg_ctp_res'] = ""
        line['min_ctp_ref'] = ""
        line['min_ctp_res'] = ""    
        line['max_ctp_ref'] = ""
        line['max_ctp_res'] = ""
   
    return line

def runtime_compare(dir):
    """compare all reference/result pairs and summarize, return collection of results"""
 
    headline = {'name': "filename", 'total_ref': "total_ref", 'total_res': "total_res", 'opt_ref': "opt_ref", 'opt_res': "opt_res", 'sync_ref': "sync_ref", 'sync_res': "sync_res", 'sum_ctp': "sum_ctp", 'avg_ctp': "avg_ctp", 'min_ctp': "min_ctp", 'max_ctp': "max_ctp", 'remainder': "remainder"}   
    result = []

    for (path, dirs, files) in os.walk(dir):
        reference_files = [x for x in files if x.lower().find('.reference.log')!=-1]
        for fn in reference_files:
            fn_ref = os.path.join(path, fn)
            fn_res = fn_ref.replace('.reference.log', '.result.log')
            fn_head = fn.replace('.reference.log', '')
            print(fn_res)
            if os.path.exists(fn_res):                
                print('comparing logfiles..')
                line = compare_logfiles(fn_ref, fn_res)
                line['name'] = fn_head
                result.append(line)

    #now summarize
    sum = {}
    sum.setdefault('name', 0) 
    sum.setdefault('total_ref', 0)
    sum.setdefault('total_res', 0)
    sum.setdefault('opt_ref', 0)
    sum.setdefault('opt_res', 0)
    sum.setdefault('sync_ref', 0)
    sum.setdefault('sync_res', 0)
    sum.setdefault('sum_ctp_ref', 0)
    sum.setdefault('sum_ctp_res', 0)
    sum.setdefault('avg_ctp_ref', 0)
    sum.setdefault('avg_ctp_res', 0)
    sum.setdefault('min_ctp_ref', 0)
    sum.setdefault('min_ctp_res', 0)
    sum.setdefault('max_ctp_ref', 0)
    sum.setdefault('max_ctp_res', 0)
    sum.setdefault('n_ctp', 0)
    sum.setdefault('remainder_ref', 0)
    sum.setdefault('remainder_res', 0)
       
    for (entry) in result:        
        for (key, value) in entry.items():
            if not type(value) is str:
                sum[key] += value
            elif key == 'name':
                sum[key] += 1
    result.append(sum)
    return result

def write_result_file(result, filename):
    with open(filename, 'w', newline='') as csvfile:
        columns = ['name', 'total_ref', 'total_res', 'opt_ref', 'opt_res', 'sync_ref', 'sync_res', 'n_ctp', 'sum_ctp_ref', 'sum_ctp_res', 'avg_ctp_ref', 'avg_ctp_res', 'min_ctp_ref', 'min_ctp_res', 'max_ctp_ref', 'max_ctp_res', 'remainder_ref', 'remainder_res']
        writer = csv.DictWriter(csvfile, dialect='excel-tab', fieldnames=columns)        
        writer.writeheader()
        writer.writerows(result)

def parse_arguments():
    """parse arguments from command line"""
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('dir', help = 'input directory, compare .reference and .result files')
	
    return parser.parse_args()

def main():
    """main function"""
    args = parse_arguments()
    dir = args.dir
    result = runtime_compare(dir)
   	
    print(result)
    write_result_file(result, dir + "\\runtime_compare.csv")

if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
