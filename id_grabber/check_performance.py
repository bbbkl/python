# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: temp.py
#
# description
"""\n\n
    script to try something out and which is not lost after shutdown
"""

import re
import os.path
from argparse import ArgumentParser
import sys
from glob import glob


VERSION = '0.1'

def join_files(dir_name):
    files = glob(dir_name + "/*.dat")
    out = open(os.path.join(dir_name, 'combined.dat'), 'w')
    for fn in files:
        print("handled %s" % fn)
        for line in open(fn):
            out.write(line)
        out.write('\n')
    out.close()


def walk_logfiles(startdir):
    for root, dirs, files in os.walk(startdir):
        for item in [x for x in files if os.path.splitext(x)[-1].lower() == '.log']:
            pass
            #check_pairs(os.path.join(root, item))
            
def getIdPfx(line):
    if line.find('SolGoal_scheduleProcessSequenceI')!=-1:
        if line.find('begin')!=-1: 
            return 'begin'
        return 'end'
    hit = re.search(r'((?:begin|end)\s+\S+\s+\S+)', line)
    if hit:
        return hit.group(1)
    print("unhandled %s" % line)
    sys.exit(0)
            
def getId(line):
    hit = re.search("( trace_id=\d+)", line)
    if hit:
        return getIdPfx(line) + hit.group(1)
    hit = re.search("(check for cycles|SolDecomposition \d+|end\d)", line)
    if hit:
        return hit.group(1)
    hit = re.search(r'\|\s+(\S+)', line)
    if hit:
        return hit.group(1)
    print("unhandled line %s" % line)
    sys.exit(0)

def grep_performance(logfile):
    # end SolGoal_scheduleProcessSequenceI::execute scheduling process: 3L-00731565 id=705160004 dpl=5 prio=5 age=90 dd=23220 pos=1 lcp=1, abs_msecs=37678 trace_id=2 elapsed_msecs=56
    #rgx = re.compile(r'(end optimize|begin SolGoal_scheduleProcessSequenceI|end SolGoal_scheduleProcessSequenceI|end\d|start of next block|composeModel|extract in processBlocks|SolDecomposition \d+).*abs_msecs=(\d+)')
    #rgx = re.compile(r'end SolGoal_scheduleProcessSequenceI.*process:\s+(\S+).*abs_msecs=(\d+)\S+trace_id=(\d+)\S+elapsed_msecs=(\d+)')
    rgx = re.compile("abs_msecs=(\d+)")
    for line in open(logfile):
        hit = rgx.search(line)
        if hit:
            abs_msecs = hit.group(1)
            id = getId(line)
            print('%s;%s' % (id, abs_msecs))

    
def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('logfile', metavar='logfile', help='input logfile')
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
    
    grep_performance(args.logfile)
    
    



if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
