# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: temp.py
#
# description
"""\n\n
    for given directory strip all doc id suffixes, e.g. name (4722).log -> name.log
"""

import re
from glob import glob
from argparse import ArgumentParser
import os

VERSION = '0.1'


def strip_doc_id(directory):
    for path in glob(directory + "/*"):
        if not os.path.isfile(path):
            continue
        name = os.path.basename(path)
        hit = re.search(r'( \(\d+\))', name)
        if hit:
            dst = os.path.join(directory, name.replace(hit.group(1), ''))
            os.rename(path, dst)

def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('directory', metavar='directory', help='input directory')

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

    strip_doc_id(args.directory)



if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
