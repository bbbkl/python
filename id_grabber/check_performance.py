# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: temp.py
#
# description
"""\n\n
    script to try something out and which is not lost after shutdown
"""

import re
from argparse import ArgumentParser
import sys


VERSION = '0.1'

def get_id_pfx(line):
    if line.find('SolGoal_scheduleProcessSequenceI')!=-1:
        if line.find('begin')!=-1:
            return 'begin'
        return 'end'
    hit = re.search(r'((?:begin|end)\s+\S+)\s+abs_msecs', line)
    if not hit:
        hit = re.search(r'((?:begin|end)\s+\S+\s+\S+)', line)
    if hit:
        return hit.group(1)
    print("unhandled %s" % line)
    sys.exit(0)

def get_duration(line):
    hit = re.search(r'(?:elapsed_|needed )msecs=(\d+)', line)
    if hit:
        return hit.group(1)
    return ""

def get_id(line):
    hit = re.search(r"( trace_id=\d+)", line)
    if hit:
        return get_id_pfx(line) + hit.group(1)
    hit = re.search(r"(check for cycles|SolDecomposition \d+|end\d+|Change job[^,]+)", line)
    if hit:
        return hit.group(1)
    hit = re.search(r"(skip.*is_cached).*abs_msecs", line)
    if hit:
        return hit.group(1)
    hit = re.search(r"(SERVER_STATE:.*|xxx.*|since.*)\s+abs_msecs", line)
    if hit:
        return hit.group(1)
    hit = re.search(r'\|\s+(\S+)', line)
    if hit:
        return hit.group(1)
    print("unhandled line %s" % line)
    sys.exit(0)

def grep_performance(logfile, stream):
    # end SolGoal_scheduleProcessSequenceI::execute scheduling process: 3L-00731565 id=705160004 dpl=5 prio=5 age=90 dd=23220 pos=1 lcp=1, abs_msecs=37678 trace_id=2 elapsed_msecs=56
    #rgx = re.compile(r'(end optimize|begin SolGoal_scheduleProcessSequenceI|end SolGoal_scheduleProcessSequenceI|end\d|start of next block|composeModel|extract in processBlocks|SolDecomposition \d+).*abs_msecs=(\d+)')
    #rgx = re.compile(r'end SolGoal_scheduleProcessSequenceI.*process:\s+(\S+).*abs_msecs=(\d+)\S+trace_id=(\d+)\S+elapsed_msecs=(\d+)')
    rgx = re.compile(r"abs_msecs=(\d+)")
    basetime = 0
    for line in open(logfile):
        hit = rgx.search(line)
        if hit:
            abs_msecs = hit.group(1)
            ident = get_id(line)
            duration = get_duration(line)
            jobtime = ""
            if check_starttime(ident):
                jobtime = int(abs_msecs) - basetime
                basetime = int(abs_msecs)
            reltime = int(abs_msecs) - basetime
            stream.write('%s;%s;%s;%d;%s\n' % (ident, abs_msecs, duration, reltime, jobtime))

def check_starttime(ident):
    return ident.find('Change job number=') != -1

def grep_ctp_duration(logfile, stream):
    rgx = re.compile(r'abs_msecs=(\d+)')
    basetime = 0
    prev_ident = ""
    for line in open(logfile):
        hit = rgx.search(line)
        if hit:
            ident = get_id(line)
            if check_starttime(ident):
                abs_msecs = int(hit.group(1))
                jobtime = abs_msecs - basetime
                basetime = abs_msecs
                stream.write('%s;%d\n' % (prev_ident, jobtime))
                prev_ident = ident

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

    pfx = args.logfile.replace('.log', '')

    stream = open(pfx + ".performance_details.csv", "w")
    grep_performance(args.logfile, stream)

    stream = open(pfx + ".performance.csv", "w")
    grep_ctp_duration(args.logfile, stream)



if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
