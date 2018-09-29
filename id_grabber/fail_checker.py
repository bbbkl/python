# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: fail_checker.py
#
# description
from fileinput import filename
"""\n\n
    get peak counts for each customer problem out of counter file
"""

import sys
import re
import os.path
from argparse import ArgumentParser

VERSION = '0.1'

def get_counts(filename):
    """parse max counts for each customer problem out of given counter file"""
    counters = {}
    
    for line in open(filename):
        hit = re.search(r'^\./([^/]+).*(fff_f|fff_b) cnt=(\d+)', line)
        if hit:
            cid, direction, scnt = hit.groups(1)

            counters.setdefault(cid, {'fff_b' : 0, 'fff_f' : 0})

            if counters[cid][direction] < int(scnt):
                counters[cid][direction] = int(scnt)
                
        hit = re.search(r'^\./([^/]+).*dbg new peak of repeated execution\:\s+(\d+)', line)
        if hit:
            cid = hit.group(1)
            cnt = int(hit.group(2))
            counters.setdefault(cid, 0)
            if counters[cid] < cnt:
                counters[cid] = cnt
    return counters 

def pretty_print(counters):
    """pretty print"""
    for cid in sorted(counters):
        print("%-30s bwd=%-5d fwd=%d" % (cid, counters[cid]['fff_b'], counters[cid]['fff_f']))
        #print("%-30s fwd_only=%d" % (cid, counters[cid]))

def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)

    parser.add_argument('message_file', metavar='message_file', help='input message file')

    return parser.parse_args()

def main():
    """main function"""
    args = parse_arguments()

    counters = get_counts(args.message_file)
    pretty_print(counters)


if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
