# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: setup_eval.py
#
# description
"""\n\n
    evaluate setup data
"""

import sys
import re
import os.path
from argparse import ArgumentParser

VERSION = '0.1'

def grep_different_values(value_file):
    """get total numer of different values. show stat value -> #number"""
    values = {}
    for line in open(value_file):
        val = line[:-1]
        values.setdefault(val, 0)
        values[val] += 1

    for val in sorted(values):
        cnt = values[val]
        if val == '' or val == 'ActivityClass/': val = '<EMPTY_VALUE>'
        print("%s : %d" % (val, cnt))
        
    total_cnt = sum(values[val] for val in values)
    total_different_cnt = len(values)
    print('total number of values=%d, different values=%d' % (total_cnt, total_different_cnt))
    if '' in values:
        print('#EMPTY_VALUE=%d' % values[''])
    if 'ActivityClass/' in values:
        print('#EMPTY_VALUE=%d' % values['ActivityClass/'])

def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)

    parser.add_argument('value_file', metavar='value_file', help='input value file')
    
    return parser.parse_args()

def main():
    """main function"""
    args = parse_arguments()
    filename = args.value_file

    grep_different_values(filename)


if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
