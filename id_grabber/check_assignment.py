# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: check_assignment.py
#
# description

"""\n\n
    script to check assigment quality
"""
import re
from argparse import ArgumentParser
import os.path
import shutil
import sys

VERSION = '0.1'

def make_rgx(keys):
    rgx = ''
    for key in keys:
        if key == 'part':
            rgx += r"%s=(.*\|[-\d]+)" % key
        else:
            rgx += r"%s=(\S+).*" % key
    return rgx

def give_header_explanation():
    explanation = """
    no suffix = everything is fine
    --- = same due dates, probably non relevant shift
    *** = sort pos by due date is equal to sort pos by LogShowSortingOrder
    xxx = unexpected diff. problem? why?
    
    pos1 = position in cluster by due date
    pos2 = position in cluster by planned end-timepoint
    pos  = LogShowSortingOrder position
    
    """
    print(explanation)
    
class Proc:
    def __init__(self, line):
        self._line = line
        self._pos1 = -1  # duedate
        self._pos2 = -1  # planned end timepoint
        self._pos3 = -1  # position in LogShowSortingOrder
        self._tp_end = None
        self._dict = {}
        self._pos = -1
        self._is_past = False
        self._clusterhead = None
        self._fixed = False
        self.parse(line)
        
        
    def parse(self, line):
        keys = ['process', 'dpl', 'prio', 'age', 'duedate', 'part']
        hit = re.search(make_rgx(keys), line)
        if not hit:
            print(line)
            sys.exit(0)
        for idx, key in enumerate(keys):
            self._dict[key] = hit.group(idx+1) 
        self._pos = int(re.search(r"(\d+)", line).group(0))
        self._is_past = line[-2] == 'P'
        self._fixed = line.find('fixed') != -1
    
    def padded_proc(self):
        proc = self.process()
        if proc.find('/') == -1:
            return 4 * ' ' + proc
        return proc
    
    def padded_tp_end(self):
        """sample value=2022-01-13 13:15"""
        val = self.tp_end()
        if val is None:
            return "None" + 12 * ' '
        return val
    
    def __str__(self):
        fixed_info = 'fix' if self.fixed() else '   '
        if 1: # no pos2
            msg = "%s duedate=%s pos=%04d dpl=%s prio=%s age=%03d planned=%s pos1=%02d %s q=%d %s" % \
                  (self.padded_proc(), self.duedate(), self.pos(), self.dpl(), self.prio(), self.age(),
                   self.padded_tp_end(), self.pos1(), fixed_info, self.quantity(), "P" if self._is_past else " ")
        else:
            msg = "%s duedate=%s pos=%04d dpl=%s prio=%s age=%03d planned=%s pos1=%02d pos2=%02d %s q=%d %s" % \
                (self.padded_proc(), self.duedate(), self.pos(), self.dpl(), self.prio(), self.age(),
                 self.padded_tp_end(), self.pos1(), self.pos2(),
                 fixed_info, self.quantity(), "P" if self._is_past else " ")
        if self.cluster() != "" and self.cluster() != self.process()[4:]:
            msg += " cluster=%s" % self.cluster()
        return msg
        
    def cluster(self): return self._clusterhead if self._clusterhead is not None else ""
    def process(self): return self._dict['process']
    def duedate(self): return self._dict['duedate']
    def duedate_sort(self):
        # 16.04.2021
        dd = self.duedate()
        year = dd[6:]
        month = dd[3:5]
        day = dd[:2]
        return year + month + day
    def dpl(self): return self._dict['dpl']
    def part_raw(self): return self._dict['part']
    def part(self):
        #return self.part_raw() # part contains quantity -> different quantiy -> different part
        val = self.part_raw()
        #print("val_raw=%s part=%s" % (val, val[:val.rfind('|')]))
        return val[:val.rfind('|')]
    def quantity(self):
        val = self.part_raw()
        pos = val.rfind('|')
        return int(float(val[pos+1:]))
    def prio(self): return self._dict['prio'][:4]
    def age(self): return int(self._dict['age'])
    def fixed(self): return self._fixed and not self.is_demand_proxy()
    def is_demand_proxy(self): return self.pos2() == -1
    def pos(self): return self._pos
    def tp_end(self): return self._tp_end 
    def pos1(self): return self._pos1 # duedate
    def pos2(self): return self._pos2 # planned end timepoint
    def pos3(self): return self._pos3 # position in LogShowSortingOrder
    
    def set_pos1(self, val): self._pos1 = val
    def set_pos2(self, val): self._pos2 = val
    def set_pos3(self, val): self._pos3 = val
    def set_clusterhead(self, val): self._clusterhead = val
    
    def add_end(self, end):
        self._tp_end = end
     
def grep_processes(filename):
    result = []
    action = 0
    rgx = re.compile('^\s*\d+\s+\d+\s+process=.*dpl=\d.*prio=.*age=.*')
    for line in open(filename):
        if rgx.search(line):
            action = 1
            result.append(Proc(line))
        if action and re.search(r'^\s*$', line):
            break
    return result

def grep_assignment_cluster(filename):
    result = {}
    return result
    rgx_start = re.compile(r'Scheduled block with \d+ processes')
    rgx_proc = re.compile(r'^\s{20}\s+(\S.*\S+)$')
    current_cluster_head = None
    in_action = False
    for line in open(filename):
        if rgx_start.search(line):
            in_action = True
            continue
        if in_action:
            hit = rgx_proc.search(line)
            in_action = hit is not None
            if hit:
                info = hit.group(1)
                if info[0] == '*':
                    current_cluster_head = info[1:]
                    result[current_cluster_head] = current_cluster_head
                else:
                    if current_cluster_head is None:
                        raise "no cluster head with line=%s" % line
                    result[info] = current_cluster_head
    return result
    
        
def grep_cluster(filename):
    procs = grep_processes(filename)
    proc2Clusterhead = grep_assignment_cluster(filename)
    for proc in procs:
        proc_id = proc.process()[4:]
        if proc_id  in proc2Clusterhead:
            proc.set_clusterhead(proc2Clusterhead[proc_id ])
    
    cluster = {}
    for proc in procs:
        cluster.setdefault(proc.part(), [])
        cluster[proc.part()].append(proc)
    
    return cluster

def initial_sort_cluster(procs):
    """pos1 = by due date"""
    dates = []
    for proc in procs:
        sort_key = proc.duedate_sort()
        if not sort_key in dates:
            dates.append(sort_key)
    dates.sort()
    for proc in procs:
        proc.set_pos1(dates.index(proc.duedate_sort())+1)
    
def planning_sort_cluster(procs):
    """pos2 = by planned end timepoint"""
    keys = []
    for proc in procs:
        sort_key = proc.tp_end()
        if sort_key is not None and sort_key not in keys:
            keys.append(sort_key)
    keys.sort()
    for proc in procs:
        if proc.tp_end() is not None:
            proc.set_pos2(keys.index(proc.tp_end())+1)
            
def pos_sort_cluster(procs):
    """pos3 = position in LogShowSortingOrder"""
    keys = []
    for proc in procs:
        sort_key = proc.pos()
        if sort_key is not None and sort_key not in keys:
            keys.append(sort_key)
    keys.sort()
    for proc in procs:
        if proc.pos() is not None:
            proc.set_pos3(keys.index(proc.pos())+1)
    
def check_positions(procs):
    initial_sort_cluster(procs)
    planning_sort_cluster(procs)
    pos_sort_cluster(procs)
    procs.sort(key=lambda x: [x.pos1(), x.pos2()])
  
def get_suffix(proc, prev_proc):
    if proc.pos1() != proc.pos2():
        if prev_proc is not None and prev_proc.pos1() == proc.pos1():
            return "---" # same due dates, probably non relevant shift
        if proc.pos1() == proc.pos3():
            return "***" # sorted pos by due date is equal to sorted pos by LogShowSortingOrder
        if prev_proc is not None and (prev_proc.pos1()+1) != proc.pos1():
            return "xxx" # unexpected diff - why?
    return "" # everything is fine

def get_suffix2(proc, prev_proc):
    if proc.pos1() < prev_proc.pos1():
        return "*"
    return "" # everything is fine
    
def add_planning_results(cluster, headproc_file):
    proc_dict = {}
    for _, procs in cluster.items():
        for proc in procs:
            proc_dict[proc.process()] = proc
    
    first_line = True
    for line in open(headproc_file):
        if first_line:
            first_line = False
            continue
        #0 Name_Process; 1 DueDate; 2 BeginFirstAct; 3 EndLastAct; 4 NoSolution
        tokens = line.split(';')
        if(len(tokens) > 3):
            proc = tokens[0]
            proc_short = proc[4:]
            tpe = tokens[-2][:-3]
            if proc in proc_dict:
                proc_dict[proc].add_end(tpe)
            elif proc_short in proc_dict:
                proc_dict[proc_short].add_end(tpe)
    
    for part, procs in cluster.items():
        check_positions(procs)    
    
    for part, procs in sorted(cluster.items()):
        #for part, procs in cluster.items():
        proxy_cluster = 0 # procs[0].pos2() == -1
        if len(procs) > 1 and not proxy_cluster:
            print("same part, mixed quantity covers %s" % part)
            if 0:
                print("sorted by due date")
                prev_proc = procs[1]
                # show cluster sorted by due date
                for proc in procs:
                    sfx = get_suffix(proc, prev_proc)
                    print("%s %s" % (proc, sfx))
                    prev_proc = proc
                
            if 1:
                # show cluster sorted by planning date
                procs.sort(key=lambda x: [x.pos2(), x.pos1()])
                prev_proc = procs[0]
                print("sorted by planning_end_timepoint")
                for proc in procs:
                    sfx = get_suffix2(proc, prev_proc)
                    print("%s %s" % (proc, sfx))
                    prev_proc = proc
                print()
                
def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('log_file', metavar='log_file', help='input log file')

    parser.add_argument('-hi', '--headproc_info', metavar='string', # or stare_false
                      dest="headproc_file", default='', # negative store value
                      help="headproc file with start/end times")

    """
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
    cluster = grep_cluster(args.log_file)
    
    give_header_explanation()
    
    if args.headproc_file:
        add_planning_results(cluster, args.headproc_file)
    
    
    
if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
