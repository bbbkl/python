# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: stability_check.py
#
# description

"""\n\n
    script checks stability over a given time range
"""
import re
from argparse import ArgumentParser
from glob import glob
import os.path

VERSION = '0.1'

class Process:
    def __init__(self, pid, part):
        self._pid = pid
        pos = part.rfind('|')
        if pos != -1:
            self._part, self._amount = part[:pos+1], int(part[pos+1:])
        else:
            self._part, self._amound = part, 0
        #history 0=tp_log 1=pos 2=dpl 3=prio 4=age 5=duedate 6=start 7=end
        self._history = []
        
    def add_info(self, tp_info):
        self._history.append(tp_info)
        
    def get_unique_entry(self, idx):
        values = set()
        for item in self._history:
            values.add(item[idx])
        if len(values) == 0:
            return "-1"
        if len(values) == 1:
            return str(values.pop())
        return ','.join(map(lambda x: str(x), values))
        
    def get_dispolevel(self):
        return self.get_unique_entry(2)
                        
    def get_duedate(self):
        return self.get_unique_entry(5)
        
    def pprint(self):
        print("%s part=%s amount=%d dpl=%s duedate=%s" % (self._pid, self._part, self._amount, self.get_dispolevel(), self.get_duedate()))
        for tp_log, pos, dpl, prio, age, duedate, start, end in self._history:
            print("\t%s pos=%d prio=%s age=%d start=%s end=%s" % (tp_log, pos, prio, age, start, end))
     
def get_logfiles(dirname):
    logfiles = glob(dirname + "/*.log")
    return logfiles

def get_logfile_timepoint(filename):
    rgx = re.compile(r'\|\s+server\s+(?:date|time)\:\s+(\S+)')
    result = None
    with open(filename) as file:
        for line in file:
            hit = rgx.search(line)
            if hit: 
                if result is None:
                    result = hit.group(1)
                else:
                    result += " " + hit.group(1)
                    return result
    return result


def get_process_infos(filename, processes):
    tp_log = get_logfile_timepoint(filename)
    
    rgx = re.compile(r'^\s+\d+\s+(\d+)\s+process=(\S+)\s+dpl=(\d+)\s+prio=(\S+)\s+age=(\d+)\s+duedate=\s*(\S+).*part=(\S+)\s+start=(\S+)\s+end=(\S+)')
    with open(filename) as file:
        for line in file:
            hit = rgx.search(line)
            if hit:
                pos, pid, dpl, prio, age, duedate, part, start, end = hit.groups()
                fixed = line.find('fixed') != -1
                if not pid in processes:
                    processes.setdefault(pid, Process(pid, part))
                processes[pid].add_info([tp_log, int(pos), int(dpl), prio, int(age), duedate, start, end])
        
def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('logfile_dir', metavar='logfile_dir', help='directory with logfiles')

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

    processes = {}
    for fn in get_logfiles(args.logfile_dir):
        get_process_infos(fn, processes)
    for proc in processes.values():
        proc.pprint()
        print()
    
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
