# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: grep_collector_export.py
#
# description
from pywin.framework import startup

"""\n\n
    grep given collector export
"""
import re
from argparse import ArgumentParser
import os.path
import shutil

VERSION = '0.1'

def parse_res_cst(line):
    hit = re.search('activityID="([^"]+).*resourceID="([^"]+).*units="([^"]+)', line)
    id_act, id_res, units = hit.groups()
    consider_capa = line.find("considerCapa") == -1
    return ResCst(id_res, id_act, int(units), consider_capa)
    

class ResCst(object):
    """hold one resource constraint"""
    def __init__(self, res_id, act_id, units, consider_capa):
        self._res_id = res_id
        self._act_id = act_id
        self._units = units
        self._consider_capa = consider_capa
    
    def res_id(self): return self._res_id
    def act_id(self): return self._act_id
    def units(self): return self._units
    def consider_capa(self): return self._consider_capa
    
def parse_act(line):
    rgx = ''
    for tag in ['id', ' name', 'proctime', 'startPreviousPlan', 'endPreviousPlan']:
        rgx += r'%s="([^"]+).*' % tag
    #print("rgx=%s" % rgx)
    is_fixed = line.find('isFixed="1"') != -1
    is_optimized = line.find('isOptimized="1"') != -1
    params = []
    params.extend(re.search(rgx, line).groups())
    params.extend((is_fixed, is_optimized)) 
    return Act(*params)
    
class Act(object):
    """hold one activity"""
    def __init__(self, id, name, proctime, start, end, is_fixed, is_opt):
        self._id = id
        self._name = name
        self._proctime = proctime
        self._start = start[:-3]
        self._end = end[:-3]
        self._fixed = is_fixed
        self._optimized = is_opt
        
    def act_id(self): return self._id
    def start(self): return self._start
    def end(self): return self._end
    def name(self): return self._name
        
def grep_resource_constraints(filename):
    result = []
    for line in open(filename):
        if line.find("<disResReq ") != -1:
            result.append(parse_res_cst(line))
    return result

def grep_acts(filename):
    result = {}
    for line in open(filename):
        if line.find("<activity ") != -1:
            act = parse_act(line)
            result[act.act_id()] = act
    return result

def show_res_situation(res_csts, acts, id_res, range_begin, range_end):
    occupation = {}
    for res_cst in filter(lambda x: x.res_id() == id_res and x.consider_capa(), res_csts):
        act = acts[res_cst.act_id()]
        if (act.start() >= range_begin or act.end() >= range_begin) and (act.start() <= range_end or act.end() <= range_end): 
            occupation.setdefault(act.start(), [])
            occupation[act.start()].append(res_cst)
    print("start;end;act;intensity_x100")
    for start in sorted(occupation):
        for res_cst in occupation[start]:
            act = acts[res_cst.act_id()]
            print("%s %s %s %d" % (act.start(), act.end(), act.name(), res_cst.units()))
    
    
    
def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('collector_export', metavar='collector_export', help='input collector export xml file')

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

    filename = args.collector_export
    res_csts = grep_resource_constraints(filename)
    acts = grep_acts(filename)
    
    show_res_situation(res_csts, acts, 'r90190', '2021-08-02T14:00', '2021-08-02T15:00')
    #show_res_situation(res_csts, acts, 'r20913', '2021-05-11T08:47', '2021-05-11T08:47')
    #show_res_situation(res_csts, acts, 'r20913', '2021-06-02T08:57', '2021-06-02T08:57')
    
if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
