# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: temp.py
#
# description
"""\n\n
    script to try something out and which is not lost after shutdown
"""

import re
from argparse import ArgumentParser

VERSION = '0.1'


def grep_process(msgfile):
    rgx = re.compile("scheduling process:\s+(\S.*\S)\s+id=")
    result = set()
    for line in open(msgfile):
        hit = rgx.search(line)
        if hit:
            result.add(hit.group(1))
            #print(hit.group(1))
    return result

def check_for_dublicates(msgfile):
    items = set()
    rgx = re.compile(r"(^ActDispatch\s+\S+\s+\S+)")
    for line in open(msgfile):
        hit = rgx.search(line)
        if hit:
            val = hit.group(1)
            print(val)
            if val in items:
                print("dublicate='%s'" % val)
            items.add(val)
    print("#items=%d" % len(items))

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
    msgfile = args.message_file

    procs = grep_process(msgfile)
    print(','.join(procs))



if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
