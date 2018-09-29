# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: grueber.py
#
# description
"""\n\n
    script to parse sending queue logfile
"""

import re
import os.path
from argparse import ArgumentParser
import sys
from glob import glob

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


def grep_connect_times(filename):
    rgx = re.compile('^\[([^\]]+).*zzz sonic connect time (topic|queue):\s+(\d+)')
    result = []
    for line in open(filename):
        hit = rgx.search(line)
        if hit:
            timestamp = hit.group(1)
            topic_or_queue = hit.group(2)
            duration = int(hit.group(3))
            
            result.append((timestamp, topic_or_queue, duration))
    return result    
    
def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('logfile', metavar='logfile', help='input logfile sending queue')
    parser.add_argument('-m', '--mat-id', metavar='string', # or stare_false
                      dest="id_mat", default='', # negative store value
                      help="material id to grep")
    parser.add_argument('-c', '--count', metavar='N', type=int, # or stare_false
                      dest="count", default=0, # negative store value
                      help="count")
    parser.add_argument('-p', '--pattern', metavar='string', # or stare_false
                      dest="pattern", default='xxx', # negative store value
                      help="search pattern within logfile")
    return parser.parse_args()        
        
def main():
    """main function"""
    args = parse_arguments()
    filename = args.logfile
    
    items = grep_connect_times(filename)
    for ts, topic_or_queue, duration in items:
        print("%s %s %d" % (ts, topic_or_queue, duration))
    



if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
