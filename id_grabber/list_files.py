# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: temp.py
#
# description
"""\n\n
    for given start dir list full path name of all files within it and within sub dirs.
"""

import os.path
from argparse import ArgumentParser

VERSION = '0.1'

    
def list_files(start_dir):
    #extensions = ('.log')
    for root, dirs, files in os.walk(start_dir):
        #relevant_files = list(filter(lambda x: os.path.splitext(x)[1] in extensions, files))
        for item in files:
            print(os.path.join(root, item))
    

    
def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('start_dir', metavar='start_dir', help='start dir')
    return parser.parse_args()        
        
def main():
    """main function"""
    args = parse_arguments()
    list_files(args.start_dir)
    
if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
