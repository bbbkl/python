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
from datetime import datetime
from itertools import islice
from glob import glob

VERSION = '0.1'

def build_regex(keys):
    pattern = r"(%s)" % "|".join(keys)
    #print(pattern)
    #sys.exit(1)
    return pattern

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

def rename_or_copy_related_logs(outdir, path_prefix, idx):
    """get latest two files which match search pattern, rename them"""
    files = glob(path_prefix + "*log")
    num_targets = min(2, len(files))
    res = []
    if num_targets:
        targets = reversed(files[-num_targets:])
        for name in targets:
            rename_or_copy(outdir, name, idx)
            res.append(name)
    return res

def get_report_file(outdir, logfile):
    return  os.path.join(outdir, os.path.basename(logfile) + "_report")

def report(outdir, logfile, related_logs, idx):
    report_file = get_report_file(outdir, logfile)
    out = open(report_file, "a")
    out.write("%d\n" % idx)
    for item in related_logs:
        out.write("\t%s\n" % item)
    out.close()

def rename_or_copy(outdir, filename, idx, n = 1):
    """try for n seconds to rename file, otherwise copy it"""
    dst = os.path.join(outdir, "%d.%s" % (idx, os.path.basename(filename)))
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
    
def supervise_logfile(logfile, path_pfx, start_idx, outdir, sleep_secs=10):
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
    keywords = ['Ein kritischer Fehler ist aufgetreten', ]
    idx = 0
    while True:
        if found:
            print("line idx=%d" % found)
            found_items.append(found)
            related_logs = rename_or_copy_related_logs(outdir, path_pfx, found)
            report(outdir, logfile, related_logs, found)
            start_idx = found + 20
            return

        found = search_log(logfile, start_idx, keywords)
        if not found:
            time.sleep(sleep_secs)
        if idx % 18 == 0:
            with open(get_report_file(outdir, logfile), 'a') as out:
                out.write("%s\n" % datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                out.close()
        idx += 1
            
   
def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('logfile', metavar='logfile', help='main logfile to supervise')
    parser.add_argument('outdir', metavar='outdir', help='output directory for logfiles of this script')

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
    
    supervise_logfile(args.logfile, args.path_pfx, args.offset, args.outdir)
    return 1
    
    
if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
