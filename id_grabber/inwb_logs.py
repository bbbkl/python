# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: inwb_logs.py
#
# description
"""\n\n
    script to parse inwb logfile and strip relevant parts
"""

import re
from argparse import ArgumentParser

VERSION = '0.1'

def grep_start_stop(filename):
    rgx = re.compile('(starting\.\.\.|\.\.\.startup complete|Shutdown initiated|Exiting\.\.\.)')
    rgx_newline_before = re.compile('starting\.\.\.')
    rgx_newline_after = re.compile('\.\.\.startup')
    for line in open(filename):
        hit = rgx.search(line)
        if hit:
            if rgx_newline_before.search(line):
                print('\n')
            print(line[:-1])  
            if rgx_newline_after.search(line):
                print('\n')
    
def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('logfile', metavar='logfile', help='input logfile sending queue')
    return parser.parse_args()        
        
def main():
    """main function"""
    args = parse_arguments()
    filename = args.logfile
    
    grep_start_stop(filename)


if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
