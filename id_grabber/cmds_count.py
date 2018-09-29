# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: cmds_count.py
#
# description
"""\n\n
    take message_file an count contained commands, print overview to console
"""

import sys
import re
import os.path
from argparse import ArgumentParser

VERSION = '0.1'

def parse_commands( messagefile, start_line, end_line ):
    """count contained commands"""
    result = {}
    idx = 0
    rgx = re.compile(r'^2\t\d+\t(.*)')
    for line in open(messagefile):
        idx += 1
        if idx < start_line: continue
        if end_line != -1 and idx >= end_line: break
        hit = rgx.search(line)
        if hit:
            cmd = hit.group(1)
            result.setdefault(cmd, 0)
            result[cmd] += 1
            
    return result

def parse_commandsCtp( messagefile ):
    """count contained commands"""
    stats = {}
    idx = 0
    rgx = re.compile(r'^2\t\d+\t(.*)')
    line_start = 0
    prev_line = ''
    ctp_count = 0
    for line in open(messagefile):
        idx += 1
        
        if line.find('DEF_ERPCommandgetSolutionCtpProd__') != -1:
            ctp_count += 1
            print("\n\nobj count between lines %d and %d, ctp_no=%d process=%s" % (line_start, idx, ctp_count, prev_line[2:-1]))
            pretty_print(stats)
            stats = {}
            line_start = idx
            continue
        
        hit = rgx.search(line)
        if hit:
            cmd = hit.group(1)
            stats.setdefault(cmd, 0)
            stats[cmd] += 1

        prev_line = line
        
def pretty_print(stats):
    """pretty print dict to console"""
    for key in stats:
        print("%s\t%d" % (key, stats[key]))

def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)

    parser.add_argument('message_file', metavar='message_file', help='input message file')
    parser.add_argument('-s', '--startline', metavar='N', type=int,
                      dest="startline", default=0,
                      help="skip lines before given startline")
    parser.add_argument('-e', '--endline', metavar='N', type=int,
                      dest="endline", default=-1,
                      help="skip lines after reaching endline")
    parser.add_argument('-c', '--ctp', action="store_true", # or store_false
                      dest="ctp", default=False) 

    return parser.parse_args()

def main():
    """main function"""
    args = parse_arguments()
    filename = args.message_file
    
    if args.ctp:
        parse_commandsCtp(filename)
        return
    
    stats = parse_commands(filename, args.startline, args.endline)
    pretty_print(stats)

if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
