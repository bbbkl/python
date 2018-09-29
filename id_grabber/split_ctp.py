# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: split_ctp.py
#
# description
"""\n\n
    split given messagefile into separate ctp parts
"""

import re
import os.path
from argparse import ArgumentParser

VERSION = '0.1'


def test_encoding(message_file):
    """check for file encoding"""
    encodings = ["UTF-8", "ISO-8859-1", "latin-1"]
    
    if not os.path.exists(message_file):
        raise FileNotFoundError(message_file)
    
    for item in encodings:
        try:
            for line in open(message_file, encoding=item):
                pass
            return item
        except:
            pass
        
    raise ("Cannot get right encoding, tried %s" % str(encodings))
        
def split_ctp(filename):
    """split filename into startup, ctp_001, ctp_002, ..."""
    cnt = 0
    fn_out = filename + '%03d' % cnt
    out = open(fn_out, 'w')
    prev_line = None 
    for line in open(filename):
        do_separate = (line.find('2\t110') == 0) # 110 DEF_ERPCommandCheckErpID__________
        if do_separate:
            if cnt > 0:
                out.close()
                fn_out = filename + '%03d' % cnt
                out = open(fn_out, 'w')
            cnt += 1
        if prev_line is not None: 
            out.write("%s" % prev_line)
        prev_line = line
    if prev_line is not None:
        out.write("%s" % prev_line)
    out.close()
        
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
    filename = args.message_file
    
    split_ctp(filename)

if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
