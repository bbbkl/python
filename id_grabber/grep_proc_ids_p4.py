# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: id_grabber.py
#
# description
"""\n\n
    take collector export as input and grep related process ids for given id of type xxx
"""

import sys
import re
import os.path
from argparse import ArgumentParser

VERSION = '0.1'

def grep_ordered_proc_ids(logfile):
    """for given logfile get ordered process ids"""
    # 5.2 line:   46  158 process LA-01194016          dispolevel:  1 
    # 6.1 line: begin SolGoalSchedulePrioI::execute scheduling process: p98738 LA-00016297
    proc_ids = set()
    rgx_section_start = re.compile(r"Scheduled block with")
    rgx_proc = re.compile(r"^\s+\*?(\S+)")
    in_section = False
    for line in open(logfile):
        if not in_section and rgx_section_start.search(line):
            in_section = True
            continue
        if in_section:
            hit = rgx_proc.search(line)
            in_section = hit is not None
            if hit:
                proc_ids.add(hit.group(1))
            
    return proc_ids

def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)

    parser.add_argument('message_file', metavar='message_file', help='input message file')
    parser.add_argument('-rid', '--res_id', metavar='string',
                      dest="res_id", default='',
                      help="grep process ids of processes which require given resource id")
    parser.add_argument('--fixed_ids', action="store_true", # or store_false
                      dest="fixed_ids", default=False, # negative store value
                      help="grep ids of completely fixed processes out of message_file")
    parser.add_argument('--partproc_duedate', action="store_true", # or store false)
                        dest='partproc_duedate', default=False, 
                        help="grep ids of processes which contain a partproc with own duedate")

    return parser.parse_args()

def main():
    """main function"""
    args = parse_arguments()
    filename = args.message_file

    process_ids = grep_ordered_proc_ids(filename)
    print(','.join(process_ids))
    return 0



if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
