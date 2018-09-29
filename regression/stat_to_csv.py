# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: stat_to_csv.py
#
# description
"""\n\n
    recursevly watch out for result.log / reference.log pairs.
    compare each pair for specified criteria.
    append results to csv output.
"""

import sys
import re
import os.path
from datetime import datetime
from argparse import ArgumentParser

VERSION = '0.1'

def make_regex(keys):
    result = {}
    for key in keys:
        rgx = re.compile(r'(%s)(?:.*:)?\s*(\S+)' % key)
        result[rgx] = key
    return result

def parse_head_info(stream, keys):
    rgx_dict = make_regex(keys)
    rgxDone = []
    key_flag = False
    result = {}
    while stream:
        line = stream.readline()
        key_flag |= line.find('=== Processing statistics ====') != -1
        if key_flag:
            for rgx in rgx_dict:
                if rgx in rgxDone:
                    continue
                hit = rgx.search(line)
                if hit:
                    result[rgx_dict[rgx]] = hit.group(2)
                    rgxDone.append(rgx)
            if len(result) == len(keys):
                return result
    return result
            
def csv_out(filename, info_ref, info_res, keys):
    name = os.path.basename(filename)
    name = name.replace('.result.log', '').replace('testrunner_tst_', '')
    print(name)
    
    for data in (info_ref, info_res):
        line = ''
        for key in keys:
            line += data[key].replace('.', ',') + ';'
        print(line)
    print()
    print()

def grep_data(logfile, keys):
    """grep phase4 quality relevant data out of logfile"""
    stream = open(logfile)
    info = parse_head_info(stream, keys)
    return info
        

def compare_logfiles(fn_ref, fn_res, stream):
    """
    compare given file pair"""
    #print(fn_ref)
    #print(fn_res + "\n\n")
    """
    keys = ['Total proc. time with breaks', 'DLZ partproc with breaks total', 
            'Lateness total', 'Earliness total', 'computing time.*\(',
            'early:', 'in time:', 'delayed:',]
    """
    keys = [ 'computing time.*\(', ]
    
    info_ref = grep_data(fn_ref, keys)
    info_res = grep_data(fn_res, keys)
    csv_out(fn_res, info_ref, info_res, keys)
    
def get_datetime_from_string(str_time):
    return datetime.strptime(str_time, '%d.%m.%Y %H:%M:%S')
    
def get_execution_time(fn):
    rgx_time = re.compile('^(\d{2}\.\d{2}\.\d{4})\s+(\d{2}\:\d{2}\:\d{2})')
    ts1 = ts2 = None
    for line in open(fn):
        hit = rgx_time.search(line)
        if hit:
            if ts1 == None:
                ts1 = "%s %s" % (hit.group(1), hit.group(2))

            else:
                ts2 = "%s %s" % (hit.group(1), hit.group(2))
    tp1 = get_datetime_from_string(ts1)
    tp2 = get_datetime_from_string(ts2)
    delta = tp2 - tp1
    return delta.total_seconds()
    #print("%s - %s %d" % (ts1, ts2, diffsecs))
    
def get_total_execution_time(fn_ref, fn_res, stream):
    """
    get total execution time out of logfile = last timestamp - first timestamp
    """
    time_ref = get_execution_time(fn_ref)
    time_res = get_execution_time(fn_res)
    name = os.path.basename(fn_res)
    name = name.replace('.result.log', '').replace('testrunner_tst_', '')
    print('%s;%d;%d\n\n' % (name, time_ref, time_res))

def search_for_logfile_pairs(start_dir, stream):
    """watch out for result.log/reference.log pairs"""
    for (path, dirs, files) in os.walk(start_dir):
        reference_files = [x for x in files if x.lower().find('.reference.log')!=-1 and x.find('ctp')==-1]
        for fn in reference_files:
            fn_ref = os.path.join(path, fn)
            fn_res = fn_ref.replace('.reference.log', '.result.log')
            if os.path.exists(fn_res):
                #compare_logfiles(fn_ref, fn_res, stream)
                get_total_execution_time(fn_ref, fn_res, stream)

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
