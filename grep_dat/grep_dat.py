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
        return "Edge %s/%s/%s/%s -> %s/%s " % (self.proc_area(), self.proc_id(),
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
    def mat_reservation_date(self):
        return self._tokens[19]
    def __str__(self):
        #return "\t".join(self._tokens)
        return "Activitiy %s/%s/%s %s %s" % (self.proc_id(), self.partproc(), 
          self.act_pos(), self.ident_act(), self.mat_reservation_date())
         
    @classmethod 
    def cmd(cls):
        return 365  #  DEF_ERPCommandcreate_Activity_____

class ServerInfo(BaseData):
    def __init__(self, tokens):
        BaseData.__init__(self, tokens)

    def sever_date(self):
        return self._tokens[0]
    def horizon_days(self):
        return int(self._tokens[8])
    def __str__(self):
        #return "\t".join(self._tokens)
        return "ServerInfo date=%s horizon_days=%d" % (self.sever_date(), self.horizon_days())
         
    @classmethod 
    def cmd(cls):
        return 150    # DEF_ERPCommandsetServer___________
    
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
    def use_duedate(self):
        return self._tokens[22] == "1"
    def material(self):
        mat = self._tokens[3]
        if self._tokens[4] != '':
            mat += "/var=%s" % self._tokens[4]
        if self._tokens[15] != '':
            mat += "/%s" % self._tokens[15]
        return mat
    def duedate(self):
        return self._tokens[8]
    
    @classmethod 
    def cmd(cls):
        return 370  # DEF_ERPCommandcreate_Process______

class Process:
    server_start = None
    
    def __init__(self, proc_id):
        self._head_ppid = None #head_partproc.partproc_id()
        self._id = proc_id
        self._area =  None #head_partproc.proc_area()
        self._partprocs = {} #self._head_ppid : head_partproc}
        self._activities = {}
        self._edges = []
     
    def edges(self):
        return self._edges   
    def partprocs(self):
        return self._partprocs
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
    def duedate(self):
        return self.head_partproc().duedate()
    def material(self):
        return self.head_partproc().material()
    
    def add_partproc(self, partproc):
        self._partprocs[partproc.partproc_id()] = partproc
        if partproc.is_head():
            self._head_ppid = partproc.partproc_id()
            self._area = partproc.proc_area()
    def add_activity(self, activity):
        self._activities[activity.ident_act()] = activity
    def add_edge(self, edge):
        self._edges.append(edge)
        
    @classmethod 
    def server_date(cls):
        return Process.server_start  
    @classmethod 
    def set_server_date(cls, value):
        Process.server_start = value

def build_procs(items):
    procs = {}
    partprocs = filter(lambda x: isinstance(x, PartProcess), items)
    activities = filter(lambda x: isinstance(x, Activity), items)
    edges = filter(lambda x: isinstance(x, Edge), items)
    
    for server_info in filter(lambda x: isinstance(x, ServerInfo), items):
        Process.set_server_date(server_info.sever_date())
    for partproc in partprocs:
        proc_id = partproc.proc_id()
        procs.setdefault(proc_id, Process(proc_id))
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
   
def show_paths(procs):
    for proc in procs.values():
        edges = filter(lambda x: x.partproc_from() != x.partproc_to(), proc.edges())
    nodes = set()
    successors = {}
    predecessors = {}
    candidates = []
    paths = []
    for edge in edges:
        pp_from = edge.partproc_from()
        pp_to = edge.partproc_to()
        nodes.add(pp_from)
        nodes.add(pp_to)
        
        successors.setdefault(pp_from, []).append(pp_to)
        predecessors.setdefault(pp_to, []).append(pp_from)
    for node in filter(lambda x: x not in successors, nodes):
        candidates.append([node,])
    while candidates:
        curr = candidates.pop()
        leftmost = curr[0]
        if not leftmost in predecessors:
            paths.append(curr)
        else:
            for node in predecessors[leftmost]:
                candidates.append([node] + curr)
    
    
    rootToNodes = {}
    for path in paths:
        root = path[-1]
        rootToNodes.setdefault(root, set()).update(path)
    
    rootOverlapsWith = {}
    #rootOverlapNodes = {}
    for lhs in rootToNodes:
        nodes_lhs = rootToNodes[lhs]
        for rhs in rootToNodes:
            if lhs != rhs:
                nodes_rhs = rootToNodes[rhs]
                mix = nodes_lhs.intersection(nodes_rhs)
                if mix:
                    rootOverlapsWith.setdefault(lhs, set()).add(rhs)
                    print("root1=%s root2=%s %s" % (lhs, rhs, mix))
    
    #print(rootOverlapsWith)
    
    prev_root = None
    for path in paths:
        root = path[-1]
        if root != prev_root:
            print(40 * "=")
            nodes = sorted(rootToNodes[root])
            print("partprocs of partproc %s with duedate #partprocs=%d isolated=%s\n%s\n" % 
                  (root, len(nodes), "0" if root in rootOverlapsWith else "1", nodes))
            prev_root = root
        print(path)
     
        
def show_timebounds(items):
    server_info =  next(x for x in items if isinstance(x, ServerInfo))
    server_date = server_info.sever_date()
    activities = filter(lambda x: isinstance(x, Activity), items)
    special_acts = filter(lambda x: x.mat_reservation_date() != server_date, activities)
    print("server date=%s" % server_date)
    for act in special_acts:
        print(act)
        
def date_less_eq(date1, date2):
    if date1[6:10] < date2[6:10]: return True
    if date1[6:10] > date2[6:10]: return False
    if date1[3:4] < date2[3:4]: return True
    if date1[3:4] > date2[3:4]: return False
    if date1[0:1] < date2[0:1]: return True
    if date1[0:1] > date2[0:1]: return False
    return True   
                     
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

    items = parse_messagefile(args.message_file, [PartProcess, Activity, Edge, ServerInfo])
    procs = build_procs(items)

    if 0: # stadler timebounds
        show_timebounds(items)
        sys.exit(0)
    
    if 1:
        show_paths(procs)
        return 0
        
    if 0: # wds monster procs
        act2proc = {}
        for proc in procs.values():
            act_cnt = proc.act_cnt()
            act2proc.setdefault(act_cnt, [])
            act2proc[act_cnt].append(proc)
        for cnt in sorted(act2proc):
            for proc in act2proc[cnt]:
                edges = proc.edges()
                # for edge in edges: print("from=%s to=%s" % (edge.partproc_from(), edge.partproc_to()))
                outer_edges = filter(lambda x: x.partproc_from() != x.partproc_to(), edges)
                outer_cnt = sum(1 for _ in outer_edges)
                use_duedate_cnt = sum(1 for _ in  filter(lambda x: x.use_duedate(), proc.partprocs().values()))
                pp_mat_cnt = proc.pproc_cnt() - use_duedate_cnt
                print("#acts=%d pprocs=%d #pp_with_duedate=%d #pp_mat=%d #aobs=%d #aobs_outer=%d proc=%s" % 
                      (cnt, proc.pproc_cnt(), use_duedate_cnt, pp_mat_cnt, len(edges), outer_cnt, proc.proc_id()))
        sys.exit(0)
    
    temp_procs = dict(filter(lambda x: x[1].is_temp(), procs.items()))
    temp_proc_cnt = sum(1 for _ in temp_procs)
    
    materials = {}
    temp_past_dd_cnt = 0
    for item in temp_procs.values():
        if date_less_eq(item.duedate(), Process.server_date()):
            temp_past_dd_cnt += 1
        mat = item.material()
        if not mat in materials:
            materials.setdefault(mat, 0)
        materials[mat] += 1

    single_mats = filter(lambda x: materials[x] == 1, materials)
    cnt_single_mat = sum(1 for _ in single_mats)
    
    print("\ntotal number of #procs=%d" % len(procs) )
    print("#temp_procs=%d (%0.1f %% of all procs)" % (temp_proc_cnt, 100 * temp_proc_cnt / len(procs)))
    print("#temp procs with due date <= server time=%d (%0.1f %%)" % (temp_past_dd_cnt, 100 * temp_past_dd_cnt / temp_proc_cnt))
    print("temp procs produce number of different materials: #mat=%d" % len(materials))
    print("number of materials produced only once by a temp proc: #mat_single=%d (%0.1f %%)" % (cnt_single_mat, cnt_single_mat*100/len(materials))) 
     
    print("\n\npart/mrp_area    #temp_procs which produce this part")
    for mat, mat_cnt in sorted(materials.items(), key=operator.itemgetter(1), reverse=True):
        print("%s    %d" % (mat, mat_cnt)) 
    
if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
    
    
