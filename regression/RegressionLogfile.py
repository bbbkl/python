# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: RegressionLogfile.py
#
# description
"""\n\n
    regression log file pair reference/result
"""

from argparse import ArgumentParser
from datetime import datetime
import re
import os
from RegressionResultCodes import Regr
import RegressionUtil


VERSION = '1.0'

def get_datetime_from_string(str_time):
    try:
        return datetime.strptime(str_time, '%d.%m.%Y %H:%M:%S')
    except:
        print("failed input str_time=%s" % str_time)
        return -1

def pretty_format_secs(seconds):
    if seconds == -1:
        return "-1"
    hours = int(seconds / (60 * 60))
    rest = seconds % (60 * 60)
    minutes = int(rest / 60)
    secs = rest % 60
    return "%02d:%02d:%02d" % (hours, minutes, secs)

class RegressionLogfile:
    """regression logfile pair based on a message file initialized with reference.log."""
    def __init__(self, reference_file):
        self.reference_file = reference_file
        self.encoding_cache = {}

    def __str__(self):
        msg = "RegressionLogfile\n\tref='%s %d'\n\tres='%s %d'" % \
            (self.get_reference_file(),
             self.get_total_seconds(self.get_reference_file()),
             self.get_result_file(),
             self.get_total_seconds(self.get_result_file()) )
        #for item in self.get_errors(self.get_reference_file()):
        #    msg += "\n\te-r-r-o-r %s" % item
        for item in self.get_warnings(self.get_reference_file()):
            msg += "\n\tw-a-r-n-i-n-g %s" % item
        config = self.get_active_conifg(self.get_reference_file())
        for key in config:
            msg += "\n\tc-o-n-f-i-g %s=%s" % (key, config[key])
        return msg

    def create_report(self):
        ref, res = self.get_reference_file(), self.get_result_file()
        ref_secs = self.get_total_seconds(ref)
        res_secs = self.get_total_seconds(res)
        report = "\n\ttime reference=%s result=%s" % (pretty_format_secs(ref_secs), pretty_format_secs(res_secs))
        ref_ctp_msecs = self.get_avg_ctp_msecs(ref)
        res_ctp_msecs = self.get_avg_ctp_msecs(res)
        if ref_ctp_msecs and res_ctp_msecs:
            pct = round(res_ctp_msecs * 100 / max(ref_ctp_msecs, 1))
            report += "\n\tavg msecs ctp reference=%d result=%d (%d%%)" % (ref_ctp_msecs, res_ctp_msecs, pct)
        ref_mem = self.get_max_memory_footprint(ref)
        res_mem = self.get_max_memory_footprint(res)
        report += "\n\tmemory [gb] reference=%s result=%s" % (ref_mem, res_mem)
        errs_ref, errs_res = self.get_errors(ref), self.get_errors(res)
        if errs_ref:
            report += "\n\terrors in reference:"
            for item in errs_ref:
                report += "\n\t\t%s" % item
        if errs_res:
            report += "\n\terrors in result:"
            for item in errs_res:
                report += "\n\t\t%s" % item
        wcnt_ref, wcnt_res = len(self.get_warnings(ref)), len(self.get_warnings(res))
        if wcnt_ref != wcnt_res:
            report += "\n\t#warnings differs #ref=%d #res=%d" % (wcnt_ref, wcnt_res)
        report += self.get_config_diff()
        report += self.get_key_value_diffs()
        return report

    def get_config_diff(self):
        diff = ""
        if os.path.exists(self.get_reference_file()) and os.path.exists(self.get_result_file()):
            ref = self.get_active_conifg(self.get_reference_file())
            res = self.get_active_conifg(self.get_result_file())
            for key in ref:
                if not key in res:
                    diff += "\n\t\t%s reference=%s, result=default" % (key, ref[key])
                elif ref[key] != res[key]:
                    diff += "\n\t\t%s reference=%s result=%s" % (key, ref[key], res[key])
            for key in res:
                if not key in ref:
                    diff += "\n\t\t%s reference=default, result=%s" % (key, res[key])
            if diff:
                diff = "\n\tconfiguration differs" + diff
        return diff

    def get_reference_file(self):
        return self.reference_file
    def get_result_file(self):
        """result file is based on refence file"""
        return self.reference_file.replace('.reference.', '.result.')

    def get_result(self):
        """dummy implementation so far"""
        ref, res = self.get_reference_file(), self.get_result_file()
        if self.get_errors(ref) or self.get_errors(res):
            return Regr.FAILED if self.get_errors(res) else Regr.DIFF
        if len(self.get_warnings(ref)) < len(self.get_warnings(res)):
            return Regr.DIFF
        if self.get_key_value_diffs():
            return Regr.DIFF
        return Regr.OK

    def get_active_conifg(self, logfile):
        result = {}
        if os.path.exists(logfile):
            key_config_start = '- active config'
            rgx_config_entry = re.compile(r'\s+\([^)]+\)\s+(\S+)=(\S*)')
            in_config = False
            for line in open(logfile, encoding=self.get_encoding(logfile)):
                if in_config:
                    hit = rgx_config_entry.search(line)
                    in_config = hit is not None
                    if in_config:
                        result[hit.group(1)] = hit.group(2)
                        continue
                    break
                in_config = line.find(key_config_start) != -1
        return result

    def get_errors(self, logfile):
        candidates = self.get_pattern('Error', logfile)
        false_positives = ["'solthrowonerror'", 'SolThrowOnError=1', '?ERROR?']
        return self.filter_false_positives(candidates, false_positives)

    def get_warnings(self, logfile):
        candidates = self.get_pattern('Warning', logfile)
        false_positives = []
        return self.filter_false_positives(candidates, false_positives)

    @classmethod
    def get_keys(cls):
        """watchout for these keys within logfile"""
        return ['decompositions all/unexpected:',
                'no solution:',
                'early:',
                'in time:',
                'delayed:',
                'Lateness total/avg/max:',
                'Earliness total/avg/max:']

    @classmethod
    def make_key_val_rgx(cls, keys):
        pattern = r"^\s*(" + keys[0]
        for key in keys:
            pattern += "|%s" % key
        pattern += r")\s+(\d.*)$"
        return re.compile(pattern)

    @classmethod
    def pretty_val(cls, val):
        hit = re.search(r'(\t|\s{2})', val)
        while hit:
            val = val.replace(hit.group(1), ' ')
            hit = re.search(r'(\t|\s{2})', val)
        val = val.replace('( ', '(')
        return val

    def get_key_value_pairs(self, logfile):
        result = {}
        keys = self.get_keys()
        rgx = self.make_key_val_rgx(keys)
        if os.path.exists(logfile):
            for line in open(logfile, encoding=self.get_encoding(logfile)):
                hit = rgx.search(line)
                if hit:
                    key = hit.group(1)
                    val = hit.group(2)
                    result[key] = self.pretty_val(val)
                    keys.remove(key)
                    if len(keys) == 0:
                        break
                    rgx = self.make_key_val_rgx(keys)
            result.update(self.get_resource_utilization_pairs(logfile))
            result.update(self.get_reason_pairs(logfile))
        for key in keys:
            result[key] = 'NOT_FOUND'
        return result

    def get_reason_pairs(self, logfile):
        """check tardiness reasons overview"""
        result = {}
        rgx = re.compile(r'#(Structure|Material|Resource|Timebound|Combi material / resource|Combi resource / resource): (.*)')
        for line in open(logfile, encoding=self.get_encoding(logfile)):
            hit = rgx.search(line)
            if hit:
                result["Reasons/#" + hit.group(1)] = hit.group(2)
        return result

    def get_resource_utilization_pairs(self, logfile):
        """
        res 7/4610 bottleneck=1 statistic_horizon=30 (days)
        activity length:  median=282 average=473 average_short=18 average_long=2076 standard_deviation=524
        usage:  area_inital=21180 free=7562 (35.7%) average=1.12 standard_deviation=0.40
        """
        result = {}
        key = None
        rgx_key = re.compile(r"(res\s.*)bottleneck=1\s+statistic_horizon=(\d+)")
        rgx_val = re.compile(r"(free=[^=]+)\s\S+=")
        for line in open(logfile, encoding=self.get_encoding(logfile)):
            if key is None:
                hit = rgx_key.search(line)
                if hit:
                    key = hit.group(1) + hit.group(2) + " days"
            else:
                hit = rgx_val.search(line)
                if hit:
                    result[key] = hit.group(1)
                    key = None
        return result

    def get_key_value_diffs(self):
        diff = ""
        if os.path.exists(self.get_reference_file()) and os.path.exists(self.get_result_file()):
            ref = self.get_key_value_pairs(self.get_reference_file())
            res = self.get_key_value_pairs(self.get_result_file())
            for key in ref:
                if key in res and ref[key] != res[key]:
                    diff += "\n\t\t%s '%s' <-> '%s'" % (key, ref[key], res[key])
            if diff:
                diff = "\n\tkey value pairs differ (ref <-> res)" + diff
        return diff

    def filter_false_positives(self, candidates, false_positives):
        result = []
        for item in candidates:
            found = False
            for key in false_positives:
                if item.find(key) != -1:
                    found = True
                    break
            if not found:
                result.append(item)
        return self.truncate_timestamp(result)

    @classmethod
    def truncate_timestamp(cls, candidates):
        result = []
        rgx_timestamp = re.compile(r'^[^|]*\|(.*)')
        for line in candidates:
            hit = rgx_timestamp.search(line)
            if hit:
                result.append(hit.group(1))
            else:
                result.append(line)
        return result

    def get_pattern(self, pattern, logfile):
        result = []
        if logfile:
            rgx = re.compile(pattern, re.IGNORECASE)
            for line in open(logfile, encoding=self.get_encoding(logfile)):
                hit = rgx.search(line)
                if hit:
                    result.append(line[:-1])
        return result

    def get_avg_ctp_msecs(self, logfile):
        """get avg ctp execution time in msecs or None"""
        if logfile is None or not os.path.exists(logfile):
            return None
        rgx = re.compile(r'calcCtp Nr=(\d+).*abs_msecs=(\d+)')
        start_tp = None
        for line in open(logfile, encoding=self.get_encoding(logfile)):
            hit = rgx.search(line)
            if hit:
                if start_tp is None:
                    start_no, start_tp = map(int, hit.groups())
                end_no, end_tp = map(int, hit.groups())
        if start_tp is None:
            return None
        return round((end_tp - start_tp) / (end_no- start_no + 1))

    def get_total_seconds(self, logfile):
        """differnce last - first timestamp"""
        if logfile is None or not os.path.exists(logfile):
            return -1
        # thread id prefix before timestamp
        rgx_time = re.compile(r'^\d*\|?(\d{2}\.\d{2}\.\d{4})\s+(\d{2}\:\d{2}\:\d{2})')
        ts1 = ts2 = None
        for line in open(logfile, encoding=self.get_encoding(logfile)):
            hit = rgx_time.search(line)
            if hit:
                ts1 = "%s %s" % (hit.group(1), hit.group(2))
                break
        for line in reversed(list(open(logfile, encoding=self.get_encoding(logfile)))):
            hit = rgx_time.search(line)
            if hit:
                ts2 = "%s %s" % (hit.group(1), hit.group(2))
                break
        tp1 = get_datetime_from_string(ts1)
        tp2 = get_datetime_from_string(ts2)
        delta = tp2 - tp1
        return delta.total_seconds()

    def get_encoding(self, filename):
        """check which encoding is used within given file"""
        if not filename in self.encoding_cache:
            self.encoding_cache[filename] = RegressionUtil.test_encoding(filename)
        return self.encoding_cache[filename]
    
    def get_max_memory_footprint(self, logfile):
        if logfile is None or not os.path.exists(logfile):
            return -1
        # thread id prefix before timestamp
        rgx_memory = re.compile(r'(?:memory used|peak memory)\s+\[gb\]\:\s+(\d+\.\d+)')
        for line in reversed(list(open(logfile, encoding=self.get_encoding(logfile)))):
            hit = rgx_memory.search(line)
            if hit:
                return hit.group(1)
        return -1.0
    
def parse_arguments():
    """parse commandline arguments"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('reference_file', metavar='reference_file', help='input regression reference logfile')
    return parser.parse_args()

def main():
    """main function"""
    args = parse_arguments()

    item = RegressionLogfile(args.reference_file)
    print(item)
    print("result=%s" % item.get_result())
    #print("avg ctp duration=%s msecs" % item.get_avg_ctp_msecs(args.reference_file))
    print(item.get_config_diff())
    #print(item.create_report())

if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
