# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: temp.py
#
# description
"""\n\n
    script to try something out and which is not lost after shutdown
"""

import re
from argparse import ArgumentParser
import os.path
import shutil
import time
from itertools import islice
from glob import glob

VERSION = '0.1'

#10:30:59.098
#10:30:59.235
#10:31:00.371

class Timepoint:
    def __init__(self, hour, minute, second, msec):
        self._hour = hour
        self._minute = minute
        self._second = second
        self._msec = msec

    def hour(self): 
        return self._hour

    def __str__(self):
        return "%02d:%02d:%02d.%03d" % (self._hour, self._minute, self._second, self._msec)
    
    def get_msecs(self):
        return (((self._hour * 60 + self._minute) * 60) + self._second) * 1000 + self._msec

def get_diff(tp1, tp2):
    msecs1 = tp1.get_msecs()
    msecs2 = tp2.get_msecs()

    if msecs2 < msecs1:
        if tp1.hour() == 23 and tp2.hour() == 0:
            msecs2 += 24 * 60 * 60 * 1000
        #else:
        #    print(tp1, tp2)

    return msecs2 - msecs1

def grep_longfiles(filename):
    diff_dict = {}
    prev_tp = None
    for line in open(filename):
        hit = re.search(r'(\d{2}):(\d{2}):(\d{2})\.(\d{3})$', line)
        if hit:
            #h2, m2, s2, msecs2 = hit.groups()
            tp = Timepoint(int(hit.group(1)), int(hit.group(2)), int(hit.group(3)), int(hit.group(4)))
            #print(tp)
            if prev_tp is not None:
                diff = get_diff(prev_tp, tp)
                if diff > 1000:
                    # 02.11.2020
                    date_hit = re.search(r'(\d{2}\.\d{2}\.\d{4})', line)
                    date = date_hit.group(1) if date_hit else '' 
                    print(diff, prev_tp, tp, date)
                diff_dict.setdefault(diff, 0)
                diff_dict[diff] += 1
                
            prev_tp = tp 
            
    return diff_dict

def pretty_print(stat):
    steps = [10, 100, 200, 300, 400, 500, 1000]
    for idx in range(len(steps)):
        lower = 0 if idx == 0 else steps[idx-1]
        upper = steps[idx]
        count = 0  
        for key in sorted(stat):
            if lower <= key and key < upper:
                count += stat[key]
        print("[%d .. %d] %d" % (lower, upper, count))
    
    for key in sorted(stat):
        if key >= steps[-1]:
            print("%d -> %d" % (key, stat[key]))

def build_regex(keys):
    pattern = r"(%s)" % "|".join(keys)
    #print(pattern)
    #sys.exit(1)
    return pattern

def grep_logcontext(logfile):
    cnt = 0
    context_len = 1000
    context = []
    keys = ['exception', '20/11/20@09:09:39', '20/11/22@11:33:40'] #, '18:00:50', 'Oct 21, 2020 15:44:03:8'], '21.10.2020 15:44:26'
    rgx = re.compile(build_regex(keys), re.IGNORECASE)
    context_cnt = 0
    out = None
    for line in open(logfile):
        if context_cnt > 0:
            context_cnt -= 1
            out.write(line)
            if context_cnt == 0:
                out.close()
                
        else:
            hit = rgx.search(line)
            if hit:
                pfx, ext = os.path.splitext(logfile)
                out = open("%s.%02d%s" % (pfx, cnt, ext), "w")
                cnt += 1
                for entry in context:
                    out.write(entry)
                context = []
                out.write(line)
                context_cnt = context_len
            else:
                context.append(line)
                if len(context) > context_len:
                    context = context[-context_len:]

def search_log(logfile, start_idx, keywords):
    """
    search log starting with line start_idx for any of provided keywords.
    return line index if successful, -1 otherwise.
    """
    rgx = re.compile(build_regex(keywords))
    with open(logfile) as stream:
        idx = start_idx
        for line in islice(stream, start_idx, None):
            idx += 1
            if rgx.search(line):
                return idx
    return None

def rename_or_copy_related_logs(path_prefix, idx):
    """get latest two files which match search pattern, rename them"""
    files = glob(path_prefix + "*log")
    num_targets = min(2, len(files))
    res = []
    if num_targets:
        targets = reversed(files[-num_targets:])
        for name in targets:
            rename_or_copy(name, idx)
            res.append(name)
    return res

def report(logfile, related_logs, idx):
    out = open(logfile + "_report", "a")
    out.write("%d\n" % idx)
    for item in related_logs:
        out.write("\t%s\n" % item)
    out.close()

def rename_or_copy(filename, idx, n = 10):
    """try for n seconds to rename file, otherwise copy it"""
    dst = os.path.join(os.path.dirname(filename), "%d.%s" % (idx, os.path.basename(filename)))
    while True:
        try:
            os.rename(filename, dst)
            return
        except:
            n -= 1
            if n < 0:
                break
            time.sleep(1)
    shutil.copyfile(filename, dst)
    
def supervise_logfile(logfile, path_pfx, start_idx, sleep_secs=10):
    """
    for given logfile skim it periodically for keywords, if a keyword pops up:
       remember line and timepoint, write this to supervisor log
       rename (or copy) related last 2 logfiles.
       if rename is not possible immediately loop for some time an make retries,
       if rename is still not possible, copy content and rename 2nd last logfile
       
       keep on skimming logfile skimming but last remembered line + n.
    """
    found_items = []
    found = None
    keywords = ["ProSQLException", "error tag = 95"]
    while True:
        if found:
            print("line idx=%d" % found)
            found_items.append(found)
            related_logs = rename_or_copy_related_logs(path_pfx, found)
            report(logfile, related_logs, found)
            start_idx = found + 20

        found = search_log(logfile, start_idx, keywords)
        if not found:
            time.sleep(sleep_secs)
   
def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('message_file', metavar='message_file', help='input message file')

    """
    parser.add_argument('-m', '--mat-id', metavar='string', # or stare_false
                      dest="id_mat", default='', # negative store value
                      help="material id to grep")
    """
    parser.add_argument('-o', '--offset', metavar='N', type=int, # or stare_false
                      dest="offset", default=0, # negative store value
                      help="line index to start with")

    parser.add_argument('-p', '--path_pfx', metavar='string', # or stare_false
                      dest="path_pfx", default='', # negative store value
                      help="path prefix of related logfile")
    
    return parser.parse_args()

def main():
    """main function"""
    args = parse_arguments()
    
    supervise_logfile(args.message_file, args.path_pfx, args.offset)
    return 1

    #grep_logcontext(args.message_file)
    
    #diff_dict = grep_longfiles(args.message_file)
    #print("\n")
    #pretty_print(diff_dict)
    
    
if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
