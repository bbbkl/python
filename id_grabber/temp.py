# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: temp.py
#
# description

"""\n\n
    script to try something out and which is not lost after shutdown
"""
import re
from argparse import ArgumentParser
import os.path
import shutil

VERSION = '0.1'

def grep_keys(filename):
    cal_items = []
    res_items = []
    prev_idx = None
    rgx = re.compile("^xxx(1|2).*'([^']*)'.*key='([^']*)'")
    for line in open(filename):
        hit = rgx.search(line)
        if hit:
            idx, val, key = hit.groups()
            if idx == "1":
                if prev_idx is None:
                    cal_items.append({})
                cal_items[-1][key] = val
            if idx == "2":
                if prev_idx is None:
                    res_items.append({})
                res_items[-1][key] = val                     
            prev_idx = idx
        else:
            prev_idx = None

    # compuare res
    for item in cal_items:
        print("#cal=%d" % len(item))
    for item in res_items:
        print("#res=%d" % len(item))
    
    cal1 = cal_items[0]
    cal2 = cal_items[1]
    for key in cal2:
        if not key in cal1:
            print("new cal2 key=%s val=%s" % (key, cal2[key])) 
    
    res1 = res_items[0]
    res2 = res_items[1]      
    for key in res2:
        if not key in res1:
            print("new res2 key=%s val=%s" % (key, res2[key])) 
        
        
def create_sample():
    base = r"D:\work\parallel_reasons\simple_tardy20\sync.single_tardy20.dat000"
    ctp = r"D:\work\parallel_reasons\simple_tardy20\sync.single_tardy20.dat001"
    
    dst = r"D:\work\parallel_reasons\simple_tardy20\simple_tardy20.dat"
    shutil.copyfile(base, dst)
    out = open(dst, "a")
    for i in range(0, 10000):
        instream = open(ctp, "r")
        out.write(instream.read()) 
    out.close()
    
def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('message_file', metavar='message_file', help='input message file')

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

    #grep_keys(args.message_file)
    create_sample()
    
    """
    diff_dict = grep_longfiles(args.message_file)
    print("\n")
    pretty_print(diff_dict)
    """
    
if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
