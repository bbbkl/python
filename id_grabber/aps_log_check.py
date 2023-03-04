# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: aps_log_check.py
#
# description
"""\n\n
    grep import info out of given aps log file(s)
"""
import re
# import re
from argparse import ArgumentParser
import os.path
# import shutil
from glob import glob
from enum import Enum

VERSION = '0.1'

def get_input(source):
    result = []
    if os.path.isfile(source):
        result.append(source)
    else:
        result = glob(os.path.join(source, "*.log"))
    return result

class Log(Enum):
    DIFF_STOCKS = 1
    CFG_CONFLICT = 2
    CFG_KEY_UNKNOWN = 3
    D_ERR = 4
    IGNORE = 5
    MBJOB00004 = 6
    STOP_CONDITION = 7
    APP_ERR = 8
    MEM_ERR = 9
    INWB_CONNECT = 10
    MIN_WBZ = 11
    CFG_ACM_UNKNOWN = 12
    INTERNAL_ERROR_DISPLAYING = 13
    UNKNOWN = 999

def get_category(line):
    categories = {r"ML_Artort with different stocks" : Log.DIFF_STOCKS,
                  r"Config-entry (.*) is defined as" : Log.CFG_CONFLICT,
                  r"Raising STOP condition" : Log.STOP_CONDITION,
                  r"d_-err-\d{5}": Log.D_ERR,
                  r"d_-app-\d{5}" : Log.APP_ERR,
                  "(solthrowonerror|SolThrowOnError)" : Log.IGNORE,
                  "unknown config key" : Log.CFG_KEY_UNKNOWN,
                  r"Unknown parameter '.*' sent by ERP": Log.CFG_ACM_UNKNOWN,
                  "mbjob00004" : Log.MBJOB00004,
                  "connecting integration workbench after 60 tries" : Log.INWB_CONNECT,
                  "Memory violation" : Log.MEM_ERR,
                  "The minimal WBZ for" : Log.MIN_WBZ,
                  "Internal error while displaying" : Log.INTERNAL_ERROR_DISPLAYING,
                }
    for key in categories:
        if re.search(key, line):
            return categories[key]
    return Log.UNKNOWN

def parse_logfile(logfile):
    cat2line = {}
    idx = 0
    with open(logfile, "r") as stream:
        for line in stream:
            idx += 1
            if re.search(r"(error|warning)", line, re.IGNORECASE):
                category = get_category(line)
                cat2line.setdefault(category, [])
                cat2line[category].append(line)
    return cat2line

def check_logs(logfiles):
    cat2line = {}
    for fn in logfiles:
        for cat, lines in parse_logfile(fn).items():
            cat2line.setdefault(cat, [])
            cat2line[cat].extend(lines)

    if Log.UNKNOWN in cat2line:
        for line in cat2line[Log.UNKNOWN]:
            print(line[:-1])
    print()
    for cat, lines in cat2line.items():
        print("#%s=%d" % (cat, len(lines)))

def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('source', metavar='source', help='input logfile or directory with logfiles')

    """
    parser.add_argument('-m', '--mat-id', metavar='string', # or stare_false
                      dest="id_mat", default='', # negative store value
                      help="material id to grep")
    parser.add_argument('-c', '--count', metavar='N', type=int, # or stare_false
                      dest="count", default=0, # negative store value
                      help="count")
    parser.add_argument('-p', '--pattern', metavar='string', # or stare_false
                      dest="pattern", default='xxx', # negative store value
                      help="search pattern within logfile")
    """
    return parser.parse_args()

def main():
    """main function"""
    args = parse_arguments()

    logfiles = get_input(args.source)
    check_logs(logfiles)
    
if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
