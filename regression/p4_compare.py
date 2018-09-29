# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: id_grabber.py
#
# description
"""\n\n
    recursevly watch out for result.log / reference.log pairs.
    compare each pair with phase-4 criteria.
    append results to csv output.
"""

import sys
import re
import os.path
from argparse import ArgumentParser

VERSION = '0.1'

def make_regex(keys):
    return [re.compile(r'(%s).*:\s+(\S+)' % key) for key in keys]

def pare_next_prio(stream):
    """parse next prio and return info dict or until end of file and return None"""
    result =  {}
    keys = ['early .as early as possible.', 'Earliness .aeap. total',
            'Earliness total',  'Lateness', 'early', 'in time', 'delayed']
    rgx_list = make_regex(keys)
    parse_flag = False
    while stream:
        line = stream.readline()
        hit = re.search(r'priority\s+([0-9\.]+)\s*$', line)
        if hit:
            result['prio'] = hit.group(1)
            parse_flag = True
            continue
        if parse_flag:
            for rgx in rgx_list:
                hit = rgx.search(line)
                if hit:
                    result[hit.group(1)] = hit.group(2)
                    break
            if len(result) > len(keys):
                return result 
    return None

def parse_head_info(stream):
    keys = ['total number', 'early', 'in time', 'delayed', 'Lateness total', 'Earliness total']
    rgx_list = make_regex(keys)
    key_flag = False
    result = {}
    while stream:
        line = stream.readline()
        key_flag |= line.find('=== Process statistics ====') != -1
        if key_flag:
            for rgx in rgx_list:
                hit = rgx.search(line)
                if hit:
                    result[hit.group(1)] = hit.group(2)
            if len(result) == len(keys):
                return result
    return result
            

def grep_data(logfile):
    """grep phase4 quality relevant data out of logfile"""
    stream = open(logfile)
    info = parse_head_info(stream)
    print(str(info))
    prio_info = pare_next_prio(stream)
    print(str(prio_info))
        

def compare_logfiles(fn_ref, fn_res, stream):
    """compare given file pair"""
    print(fn_ref)
    print(fn_res + "\n\n")
    grep_data(fn_ref)
    grep_data(fn_res)

def search_for_logfile_pairs(start_dir, stream):
    """watch out for result.log/reference.log pairs"""
    for (path, dirs, files) in os.walk(start_dir):
        reference_files = [x for x in files if x.lower().find('_reference.log')!=-1]
        for fn in reference_files:
            fn_ref = os.path.join(path, fn)
            fn_res = fn_ref.replace('_reference.log', '_result.log')
            if os.path.exists(fn_res):
                compare_logfiles(fn_ref, fn_res, stream)

def open_outstream(start_dir):
    """create output file, open it, return output stream"""
    name = start_dir + ".phase4_compare.csv"
    stream = open(name, 'w')
    return stream

def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)

    parser.add_argument('start_dir', metavar='start_dir', help='start directory')

    return parser.parse_args()

def main():
    """main function"""
    args = parse_arguments()
    start_dir = args.start_dir
    
    stream = open_outstream(start_dir)
    search_for_logfile_pairs(start_dir, stream)
   


if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
