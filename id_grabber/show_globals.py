# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: show_globals.py
#
# description
from fileinput import filename
"""\n\n
    parse given input file with lines which contain getInstance and report used globals 
"""

import sys
import re
#import os.path
from argparse import ArgumentParser

VERSION = '0.1'

def get_counts(filename):
    """parse max counts for each customer problem out of given counter file"""
    counters = {}
    
    for line in open(filename):
        hit = re.search(r'([a-zA-Z]+)::getInstance()', line)
        if hit:
            name = hit.group(1)
            counters.setdefault(name, 0)
            counters[name] += 1
            
    return counters 

def pretty_print(counters):
    """pretty print"""
    for name in sorted(counters):
        print("%-30s %d" % (name, counters[name]))
        #print("%-30s fwd_only=%d" % (cid, counters[cid]))

def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)

    parser.add_argument('data_file', metavar='data_file', help='input data file')

    return parser.parse_args()

def main():
    """main function"""
    args = parse_arguments()

    counters = get_counts(args.data_file)
    pretty_print(counters)


if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
