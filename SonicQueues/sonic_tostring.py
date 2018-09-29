# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: sonic_tostring.py
#
# description
"""\n\n
    grep defines out of sonic header file and generator toString functions
"""

import re
import os.path
from argparse import ArgumentParser

VERSION = '0.1'

def parse_sonic_codes(filename, prefix):
    rgx = re.compile(r'(%s_\S+)\s[^\-\d]*(\-?\d+)' % prefix)
    for line in open(filename):
        hit = rgx.search(line)
        if hit:
            name = hit.group(1)
            id = int(hit.group(2))
            print('case %d: return "%s";' % (id, name))
    
def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('sonic_file', metavar='sonic_file', help='input sonic jmsconstants file')
   
    return parser.parse_args()        
        
def main():
    """main function"""
    args = parse_arguments()
    filename = args.sonic_file
    
    for prefix in ['Constants', 'DeliveryMode', 'ErrorCodes', 'Message', 'Session']:    
        parse_sonic_codes(filename, prefix)
        print()
        print()


if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
