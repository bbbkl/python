# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: flat_stat.py
#
# description
from multiprocessing.sharedctypes import _new_value
"""\n\n
    convert csv items into a flat format.
"""

import sys
import re
import os.path
from argparse import ArgumentParser

VERSION = '0.1'

def convert_data(filename):
    val1 = val2 = val3 = None
    triples = []
    for line in open(filename):
        if line.strip() != '':
            new_val = line[:-1].replace(';', '')
            if val1 is None: 
                val1 = new_val
            elif val2 is None: 
                val2 = new_val
            else:
                val3 = new_val
                triples.append((val1, val2, val3))
                val1 = val2 = val3 = None
    return triples

def pretty_print(triples):
    line1 = line2 = line3 = ""
    for v1, v2, v3 in triples:
        if line1 is not "":
            line1 += '\t'
            line2 += '\t'
            line3 += '\t'
        line1 += v1
        line2 += v2
        line3 += v3
    print("sep=\t\n%s\n%s\n%s\n" % (line1, line2, line3))

def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)

    parser.add_argument('input_file', metavar='input_file', help='input file')

    return parser.parse_args()

def main():
    """main function"""
    args = parse_arguments()
    filename = args.input_file
    
    triples = convert_data(filename)
    pretty_print(triples)
   


if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise