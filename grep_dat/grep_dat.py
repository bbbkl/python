# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: BaseItem.py
#
# description
"""\n\n
    Base class for activity, ...
"""

VERSION = '0.1'

#from command_mapper import CommandMapper
import re
import sys
import operator
from argparse import ArgumentParser

class BaseData(object):
    """Base item which holds tokens and command"""
    
    def __init__(self, tokens):
        self._tokens = tokens

class Edge(BaseData):
    def __init__(self, tokens):
        BaseData.__init__(self, tokens)
    
    def proc_area(self):
        return self._tokens[0]
    def proc_id(self):
        return self._tokens[1]
    def partproc_from(self):
        return self._tokens[2]
    def partproc_to(self):
        return self._tokens[4]
    def identact_from(self):
        return self._tokens[3]
    def identact_to(self):
        return self._tokens[5]
    
    def __str__(self):
        #return "\t".join(self._tokens)
        return "Edge %s/%s/%s/%s -> %s/%s " % (self.proc_area(), self.process(), 
          self.partproc_from(), self.identact_from(), self.partproc_to(), self.identact_to())
         
    @classmethod 
    def cmd(cls):
        return 360  #  DEF_ERPCommandcreate_Constraint___

class Activity(BaseData):
    def __init__(self, tokens):
        BaseData.__init__(self, tokens)

    def proc_id(self):
        return self._tokens[1]
    def partproc(self):
        return self._tokens[2]
    def act_pos(self):
        return self._tokens[3]
    def ident_act(self):
        return self._tokens[5]
    def __str__(self):
        #return "\t".join(self._tokens)
        return "Activitiy %s/%s/%s %s " % (self.processs(), self.partproc(), 
          self.act_pos(), self.identact())
         
    @classmethod 
    def cmd(cls):
        return 365  #  DEF_ERPCommandcreate_Activity_____


class PartProcess(BaseData):
    
    def __init__(self, tokens):
        BaseData.__init__(self, tokens)
    
    def __str__(self):
        #return "\t".join(self._tokens)
        return "%s %s %s %s is_head=%s is_temp=%s" % (self._tokens[0], self._tokens[1], self._tokens[2], self._tokens[3], 
                                                      self.is_head(), self.is_temp())
    def proc_area(self):
        return self._tokens[0]
    def proc_id(self):
        return self._tokens[1]
    def partproc_id(self):
        return self._tokens[2]
    def is_head(self):
        return self._tokens[16] == "1"
    def is_temp(self):
        return self._tokens[0][0] == "C"
    def material(self):
        mat = self._tokens[3]
        if self._tokens[4] != '':
            mat += "/var=%s" % self._tokens[4]
        if self._tokens[15] != '':
            mat += "/%s" % self._tokens[15]
        return mat
    
    @classmethod 
    def cmd(cls):
        return 370  # DEF_ERPCommandcreate_Process______

class Process:
    def __init__(self, head_partproc):
        self._head_ppid = head_partproc.partproc_id()
        self._id = head_partproc.proc_id()
        self._area =  head_partproc.proc_area()
        self._partprocs = {self._head_ppid : head_partproc}
        self._activities = {}
        self._edges = []
     
    def edges(self):
        return self._edges   
    def act_cnt(self):
        return len(self._activities)
    def pproc_cnt(self):
        return len(self._partprocs)
    def is_temp(self):
        return self._area[0] == "C"
    def proc_area(self):
        return self._area
    def proc_id(self):
        return self._id
    def head_partproc(self):
        return self._partprocs[self._head_ppid]
    def material(self):
        return self.head_partproc().material()
    
    def add_partproc(self, partproc):
        self._partprocs[partproc.partproc_id()] = partproc
    def add_activity(self, activity):
        self._activities[activity.ident_act()] = activity
    def add_edge(self, edge):
        self._edges.append(edge)

def build_procs(items):
    procs = {}
    partprocs = filter(lambda x: isinstance(x, PartProcess), items)
    activities = filter(lambda x: isinstance(x, Activity), items)
    edges = filter(lambda x: isinstance(x, Edge), items)
    
    for head_partproc in filter(lambda x: x.is_head(), partprocs):
        new_proc = Process(head_partproc)
        procs[new_proc.proc_id()] = new_proc
    
    for partproc in partprocs:
        proc_id = partproc.proc_id()
        if proc_id in procs:
            procs[proc_id].add_partproc(partproc)
    for act in activities:
        proc_id = act.proc_id()
        if proc_id in procs:
            procs[proc_id].add_activity(act)
    for edge in edges:
        proc_id = edge.proc_id()
        if proc_id in procs:
            procs[proc_id].add_edge(edge)
    return procs
            
def get_key_regex(classes):
    keys = map(lambda x: str(x.cmd()), classes)
    return re.compile(r"^2\t(%s)" % "|".join(keys))

def parse_messagefile(messagefile, classes):
    items = []
    cmd2Class = {}
    for item in classes:
        cmd2Class[item.cmd()] = item
    rgx_class = get_key_regex(classes)
    rgx_dataline = re.compile("^3\s+(.*)\n?")
    dataline = None
    idx = 0
    for line in open(messagefile):
        idx += 1
        hit = rgx_class.search(line)
        if hit:
            if dataline is not None:
                cmd = int(hit.group(1))
                type = cmd2Class[cmd]
                items.append(type(dataline.split('\t')))
            dataline = None
        else:
            hit = rgx_dataline.search(line)
            if hit:
                dataline = hit.group(1)
    return items
                        
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

    items = parse_messagefile(args.message_file, [PartProcess, Activity, Edge])
    temp_procs2 = filter(lambda x: isinstance(x, PartProcess) and  x.is_temp() and x.is_head(), items)
    p2 = sum(1 for _ in temp_procs2)
    print("#p2=%d" % p2)
    
    procs = build_procs(items)
    print("#procs=%d" % len(procs))
    
    act2proc = {}
    for proc_id, proc in procs.items():
        act_cnt = proc.act_cnt()
        act2proc.setdefault(act_cnt, [])
        act2proc[act_cnt].append(proc)
    for cnt in sorted(act2proc):
        for proc in act2proc[cnt]:
            edges = proc.edges()
            outer_edges = filter(lambda x: x.partproc_from() != x.partproc_to(), edges)
            outer_cnt = sum(1 for _ in outer_edges)
            print("#acts=%d pprocs=%d #aobs=%d #aobs_outer=%d proc=%s" % (cnt, proc.pproc_cnt(), len(edges), outer_cnt, proc.proc_id()))
    sys.exit(0)
    
    temp_procs = dict(filter(lambda x: x[1].is_temp(), procs.items()))
    p1 = sum(1 for _ in temp_procs)
    print("p1=%d" % p1)
    
    #print ("#temp=%d" % len(items))
    
    materials = {}
    cnt = 0
    for id, item in temp_procs.items():
        cnt += 1
        mat = item.material()
        if not mat in materials:
            materials.setdefault(mat, 0)
        materials[mat] += 1

    single_mats = filter(lambda x: materials[x] == 1, materials)
    cnt_single_mat = sum(1 for _ in single_mats)
     
    for mat, mat_cnt in sorted(materials.items(), key=operator.itemgetter(1)):
        print("%s    %d" % (mat, mat_cnt)) 
        
    print("\n#procs=%d" % len(procs) )
    print("#temp_mat=%d #mat=%d %0.1f" % (cnt, len(materials), cnt / len(materials)))
    print("#temp_mat which occur only once=%d %0.1f" % (cnt_single_mat, cnt_single_mat*100/len(materials)))
    
if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
    
    

