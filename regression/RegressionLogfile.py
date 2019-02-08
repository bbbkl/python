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

VERSION = '1.0'

def get_datetime_from_string(str_time):
    return datetime.strptime(str_time, '%d.%m.%Y %H:%M:%S')

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
        return report
    
    def get_config_diff(self):
        diff = ""
        if os.path.exists(self.get_reference_file()) and os.path.exists(self.get_result_file()):
            ref = self.get_active_conifg(self.get_reference_file())
            res = self.get_active_conifg(self.get_result_file())
            for key in ref:
                if not key in res:
                    diff += "\n\t%s reference=%s, result=default" % (key, ref[key])
                elif ref[key] != res[key]:
                    diff += "\n\t%s reference=%s result=%s" % (key, ref[key], res[key])
            for key in res:
                if not key in ref:
                    diff += "\n\t%s reference=default, result=%s" % (key, res[key])
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
            return Regr.FAILED
        if len(self.get_warnings(ref)) < len(self.get_warnings(res)):
            return Regr.DIFF
        return Regr.OK
    
    def get_active_conifg(self, logfile):
        result = {} 
        if os.path.exists(logfile):
            key_config_start = '- active configuration -'
            rgx_config_entry = re.compile(r'\s+\([^)]+\)\s+(\S+)=(\S+)')
            in_config = False
            for line in open(logfile):
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

    def truncate_timestamp(self, candidates):
        result = []
        rgx_timestamp = re.compile('^[^|]*\|(.*)')
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
            for line in open(logfile):
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
        for line in open(logfile):
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
        rgx_time = re.compile('^(\d{2}\.\d{2}\.\d{4})\s+(\d{2}\:\d{2}\:\d{2})')
        ts1 = ts2 = None
        for line in open(logfile):
            hit = rgx_time.search(line)
            if hit:
                ts1 = "%s %s" % (hit.group(1), hit.group(2))
                break
        for line in reversed(list(open(logfile))):
            hit = rgx_time.search(line)
            if hit:
                ts2 = "%s %s" % (hit.group(1), hit.group(2))
                break
        tp1 = get_datetime_from_string(ts1)
        tp2 = get_datetime_from_string(ts2)
        delta = tp2 - tp1
        return delta.total_seconds()
        
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
    print(item.create_report())    
    
if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
