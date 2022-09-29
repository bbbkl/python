# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: BaseItem.py
#
# description
from pickle import NONE
"""\n\n
    Base class for activity, ...
"""

VERSION = '0.1'

#from command_mapper import CommandMapper
import re
import sys
import operator
import os.path
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

class ResReserved(BaseData):
    def __init__(self, tokens):
        BaseData.__init__(self, tokens)
        
    def __str__(self):
        #return "\t".join(self._tokens)
        tkn = self._tokens
        return "ResReserve identAct=%s res=%s manual=%s   start=%s/%s end=%s/%s " %  \
            (tkn[0], tkn[3], tkn[8], tkn[4], tkn[5], tkn[6], tkn[7]) 
         
    @classmethod 
    def cmd(cls):
        return 351  #  DEF_ERPCommandcreate_ResReserved__

class Resource(BaseData):
    def __init__(self, tokens):
        BaseData.__init__(self, tokens)

    def id(self):
        return "%s/%s" % (self.res_kind(), self.res())
    def res_kind(self):
        return self._tokens[0]
    def res(self):
        return self._tokens[1]
    def intensity(self):
        return float((self._tokens[5]).replace(',', '.'))
    def setup_matrix_id(self):
        if len(self._tokens) > 19:
            return self._tokens[19]
        return ""
        
    def __str__(self):
        msg = "Resource res=%-15s int=%.1f" % (self.id(), self.intensity())
        mid = self.setup_matrix_id()
        if mid:
            msg += " setup_matrix=%s" % mid
        return msg 
         
    @classmethod 
    def cmd(cls):
        return 311  #  DEF_ERPCommandcreate_M_Ressource__

class ResourceCst(BaseData):
    def __init__(self, tokens):
        BaseData.__init__(self, tokens)
    def proc_id(self):
        return self._tokens[1]
    def partproc(self):
        return self._tokens[2]
    def act_pos(self):
        return self._tokens[3]
    def ident_act(self):
        return self._tokens[7]
    def res_kind(self):
        return self._tokens[5]
    def res_id(self):
        return self._tokens[6]
    def intensity(self):
        return int(self._tokens[8])
    def is_altres(self):
        return self._tokens[9] == '1'
    def selected_res(self):
        return self._tokens[11]

    def __str__(self):
        id_act = "%s/%s/%s" % (self.proc_id(), self.partproc(), self.act_pos())
        # id_act += "/%s" % self.ident_act()
        if self.is_altres():
            return "ResourceCst %s altRes=%s selected=%s intensity=%d ident_act=%s" % (id_act,
                self.res_id(), self.selected_res(), self.intensity(), self.ident_act())
        else:
            result = "ResourceCst %s res=%s" % (id_act, self.res_id())
            if self.intensity() != 1:
                result += " intensity=%d" % self.intensity()
            return result
         
    @classmethod 
    def cmd(cls):
        return 350  #  DEF_ERPCommandcreate_Resource_____
    
    
class MaterialCst(BaseData):
    def __init__(self, tokens):
        BaseData.__init__(self, tokens)
    def proc_id(self):
        return self._tokens[1]
    def partproc(self):
        return self._tokens[2]
    def act_pos(self):
        return self._tokens[3]
    def ident_act(self):
        return self._tokens[7]
    def part(self):
        return self._tokens[5]
    def part_var(self):
        return self._tokens[6]
    def mrp_area(self):
        return self._tokens[9]
    def lot(self):
        return self._tokens[13]
    def cro(self):
        if len(self._tokens) < 17 or self._tokens[16] == '0':
            return ''
        return self._tokens[16]
    def quantity(self):
        return float(self._tokens[7].replace(',', '.'))
    def material_key(self):
        return "%s|%s|%s|%s|%s" % (self.mrp_area(), self.part(), self.part_var(), self.lot(), self.cro())

    def __str__(self):
        return "MaterialCst %s/%s/%s %s quantity=%f" % (self.proc_id(), self.partproc(), self.act_pos(), self.material_key(), self.quantity())
         
    @classmethod 
    def cmd(cls):
        return 355  #  DEF_ERPCommandcreate_Material_____    
    
def check_altsres(messagefile):
    """
    find dangling AltResCsts of fixed activities which have no selected resource
    such resources tend to be overloaded because optimizer does not know which res is selected
    """
    items = parse_messagefile(messagefile, [Activity, ResourceCst,])
    fixed_acts = filter(lambda x: isinstance(x, Activity) and x.is_frozen(), items)
    ids_fixed_acts = set()
    for act in fixed_acts:
        ids_fixed_acts.add(act.ident_act())
    unselected_res_csts = filter(lambda x: isinstance(x, ResourceCst) and x.is_altres() and x.ident_act() in ids_fixed_acts, items)
    
    #and x.selected_res()=="" \
    #    and x.ident_act() in ids_fixed_acts, items)
    #for item in ids_fixed_acts: print(item)
    
    for item in unselected_res_csts: print(item)
    
    sys.exit(0)

class Uebort(BaseData):
    def __init__(self, tokens):
        BaseData.__init__(self, tokens)
        
    def buf_time(self):
        if(len(self._tokens) > 5):
            return self._tokens[5]
        return "0";
        
    def bound_time(self):
        if(len(self._tokens) > 7):
            return self._tokens[7]
        return "0";
        
    def __str__(self):
        return "transition_place addr=%s from=%s to=%s trans=%s tu=%s buf=%s bound=%s" % (\
            self._tokens[0], self._tokens[1], self._tokens[2], self._tokens[3], self._tokens[4], self.buf_time(), self.bound_time())    
    
    @classmethod 
    def cmd(cls):
        return 316  #  DEF_ERPCommandcreate_M_UebOrt_____
    

class Uebaddr(BaseData):
    def __init__(self, tokens):
        BaseData.__init__(self, tokens)
        
    def buf_time(self):
        if(len(self._tokens) > 4):
            return self._tokens[4]
        return "0";
        
    def bound_time(self):
        if(len(self._tokens) > 6):
            return self._tokens[6]
        return "0";
        
    def __str__(self):
        return "transition_addr from=%s to=%s trans=%s tu=%s buf=%s bound=%s" % (\
            self._tokens[0], self._tokens[1], self._tokens[2], self._tokens[3], self.buf_time(), self.bound_time()) 
        
    @classmethod 
    def cmd(cls):
        return 315  #  DEF_ERPCommandcreate_M_UebAdresse_
    
def cmp_date(dt1, dt2):
    "-1 if dt1 < dt2, 1 if dt1 > dt2, 0 otherwise"
    if dt1 == dt2:
        return 0
    dt1_rev = ''.join(dt1.split('.')[::-1])
    dt2_rev = ''.join(dt2.split('.')[::-1])
    if dt1_rev < dt2_rev:
        return -1
    return 1

class PoolSelection(BaseData):
    def __init__(self, tokens):
        BaseData.__init__(self, tokens)

    def ident_act(self):
        return self._tokens[0]
    def res_kind(self):
        return self._tokens[3]
    def res(self):
        return self._tokens[4]
    def tp_start(self):
        return "%s %s" % (self._tokens[5], self._tokens[6])
    def tp_end(self):
        return "%s %s" % (self._tokens[7], self._tokens[8])

    def __str__(self):
        return "%s %s/%s start=%s end=%s" % \
               (self.ident_act(), self.res_kind(), self.res(), self.tp_start(), self.tp_end())

    @classmethod
    def cmd(cls):
        return 838  # DEF_APSCommandcreate_PoolSelection

class MbActivity(BaseData):
    def __init__(self, tokens):
        BaseData.__init__(self, tokens)

    def proc_id(self):
        return self._tokens[9]
    def partproc(self):
        return self._tokens[5]
    def ident_act(self):
        return self._tokens[0]
    def tp_start(self):
        return "%s %s" % (self._tokens[1], self._tokens[2])
    def tp_end(self):
        return "%s %s" % (self._tokens[3], self._tokens[4])

    def __str__(self):
        return "%s/%s (%s) start=%s end=%s" % (self.proc_id(), self.partproc(),
                                               self.ident_act(), self.tp_start(), self.tp_end())

    @classmethod
    def cmd(cls):
        return 840  # DEF_APSCommandcreate_ActDispatch__

class Activity(BaseData):
    _server_date = None
    
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
    def is_foreign(self):
        """foreign work = Fremdarbeit"""
        return self._tokens[4] == '1'
    def is_done(self):
        return self._tokens[29] == '1'
    def is_frozen(self):
        return self._tokens[16] == '1'
    def has_reservation(self):
        return self.server_date() != self.mat_reservation_date() and self.mat_reservation_date() != ''
    def timebound(self):
        return self._tokens[17]
    def has_timebound(self):
        return self._tokens[18] == '3' and cmp_date(self.server_date(), self.timebound()) == -1
    def has_duedate(self):
        return len(self._tokens) > 43 and self._tokens[43] != '?'
    def duedate(self):
        return self._tokens[43]
    def __str__(self):
        #return "\t".join(self._tokens)
        reservation = " reservation=" + self.mat_reservation_date() if self.has_reservation() else ""
        timebound = " timebound=" + self.timebound() if self.has_timebound() else ""
        if reservation and timebound:
            if cmp_date(reservation, timebound) < 0:
                reservation = ""
            else:
                timebound = ""
        duedate = " duedate=" + self.duedate() if self.has_duedate() else ""
        return "Activity %s/%s/%s %s%s%s%s" % (self.proc_id(), self.partproc(), 
          self.act_pos(), self.ident_act(), reservation, timebound, duedate)
         
    @classmethod
    def server_date(cls):
        return cls._server_date
    @classmethod
    def set_server_date(cls, date):     
        cls._server_date = date
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
        return "%s %s %s %s is_head=%s is_temp=%s" % (self._tokens[0], self._tokens[1], self._tokens[2], 
                                                      self._tokens[3], self.is_head(), self.is_temp())
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
    def mrp_area(self):
        return self._tokens[15]
    def part(self):
        return self._tokens[3]
    def part_var(self):
        return self._tokens[4]
    def lot(self):
        return self._tokens[21]
    def cro(self):
        if self._tokens[5] == '0':
            return '' 
        return self._tokens[5]
    def free_quantity(self):
        return float(self._tokens[17].replace(',', '.'))
    def use_duedate(self):
        return self._tokens[22] == "1"
    def material(self):
        mat = self._tokens[3]
        if self._tokens[4] != '':
            mat += "/var=%s" % self._tokens[4]
        # do not show default mrp area 0
        if self._tokens[15] != '' and self._tokens[15] != '0':
            mat += "/%s" % self._tokens[15]
        return mat
    def duedate(self):
        return self._tokens[8]
    def material_key(self):
        return "%s|%s|%s|%s|%s" % (self.mrp_area(), self.part(), self.part_var(), self.lot(), self.cro())
    
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
        self._res_csts = []
     
    def __str__(self):
        return "proc id=%s/%s quantity=%d #pp=%d #act=%d" % \
            (self.proc_area(), self.proc_id(), int(self.quantity()), self.pproc_cnt(), self.act_cnt())
     
    def edges(self):
        return self._edges
    def res_csts(self):
        return self._res_csts   
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
    def quantity(self):
        return self.head_partproc().free_quantity()
    
    def add_partproc(self, partproc):
        self._partprocs[partproc.partproc_id()] = partproc
        if partproc.is_head():
            self._head_ppid = partproc.partproc_id()
            self._area = partproc.proc_area()
    def add_activity(self, activity):
        self._activities[activity.ident_act()] = activity
    def add_edge(self, edge):
        self._edges.append(edge)
    def add_res_cst(self, res_cst):
        self._res_csts.append(res_cst)
        
    @classmethod 
    def server_date(cls):
        return Process.server_start  
    @classmethod 
    def set_server_date(cls, value):
        Process.server_start = value

class SchedulingTrigger:
    def __init__(self, line):
        self._tokens = line.split('\t')
    def __str__(self):
        return "SchedulingTrigger %s -> %s" % (self.cover_id(), self.demand_id())
    
    def pprint(self, act_lookup):
        src = self.demand_id()
        dst = self.cover_id()
        if src in act_lookup:
            src = str(act_lookup[src])
        if dst in act_lookup:
            dst = str(act_lookup[dst])
        print("SchedulingTrigger %s -> %s" % (dst, src))
        
    def demand_obj_type(self):
        return int(self._tokens[0])
    def demand_id(self):
        return self._tokens[1]
    def demand_date(self):
        return self._tokens[2]
    def cover_obj_type(self):
        return int(self._tokens[3])
    def cover_id(self):
        return self._tokens[4]

def build_procs(items):
    procs = {}
    partprocs = filter(lambda x: isinstance(x, PartProcess), items)
    activities = filter(lambda x: isinstance(x, Activity), items)
    edges = filter(lambda x: isinstance(x, Edge), items)
    res_csts = filter(lambda x: isinstance(x, ResourceCst), items)
    
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
    for res_cst in res_csts:
        proc_id = res_cst.proc_id()
        if proc_id in procs:
            procs[proc_id].add_res_cst(res_cst)
    return procs
            
def get_key_regex(classes):
    keys = map(lambda x: str(x.cmd()), classes)
    return re.compile(r"^2\t(%s)" % "|".join(keys))

def parse_sched_trigger(to_sonic_file):
    items = []
    # 2    825    DEF_APSCommandcreate_SchedTrigger_
    rgx_sched_trigger = re.compile(r"^2\t825$")
    rgx_dataline = re.compile(r"^3\s+(.*)\n?")
    data_line = NONE
    for line in open(to_sonic_file):
        hit = rgx_dataline.search(line)
        if hit:
            data_line = hit.group(1)
            continue
        
        if rgx_sched_trigger.search(line) and data_line is not None:
            items.append(SchedulingTrigger(data_line))
            data_line = None
    return items

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
    print("#PROCS=%d" % len(procs))
    for proc in procs.values():
        edges = filter(lambda x: x.partproc_from() != x.partproc_to(), proc.edges())
    nodes = set()
    successors = {}
    predecessors = {}
    candidates = []
    paths = []
    no_edge = 1
    for edge in edges:
        no_edge = 0
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
    
    print("common partprocs of two root partprocs with duedate")
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
     
    for proc in procs.values():
        if len(proc.edges()) == 0:
            pps = ','.join(proc.partprocs().keys())
            print("Isolated proc=%s partprocs=%s" % (proc.proc_id(), pps))
        
def show_forein_acts(items):
    server_info =  next(x for x in items if isinstance(x, ServerInfo))
    Activity.set_server_date(server_info.sever_date())
    activities = filter(lambda x: isinstance(x, Activity), items)
    forein_acts = filter(lambda x: x.is_foreign() and x.has_duedate() and not (x.is_frozen() or x.is_done()), activities)
    print("foreing 'lively' activities with own due date")
    for act in forein_acts:
        print(act)
        
def date_less_eq(date1, date2):
    if date1[6:10] < date2[6:10]: return True
    if date1[6:10] > date2[6:10]: return False
    if date1[3:4] < date2[3:4]: return True
    if date1[3:4] > date2[3:4]: return False
    if date1[0:1] < date2[0:1]: return True
    if date1[0:1] > date2[0:1]: return False
    return True   
       
def get_cluster(sched_trigger, start_id):
    ids = set()
    ids.add(start_id)
    while True:
        len_start = len(ids)
        for item in sched_trigger:
            if item.demand_id() in ids:
                ids.add(item.cover_id())
            if item.cover_id() in ids:
                ids.add(item.demand_id())
        if len(ids) == len_start:
            break
    cluster = []
    for item in sched_trigger:
        if item.demand_id() in ids or item.cover_id() in ids:
            cluster.append(item)
    return cluster
       
def show_sched_trigger(sched_trigger, activites):
    id_to_act = {}
    for act in activites:
        id_to_act[act.ident_act()] = act
    for item in sched_trigger:
        item.pprint(id_to_act)
   
def report_timebounds(message_file):
    """write activity info files"""
    items = parse_messagefile(message_file, [Activity, ServerInfo])
    server_info =  next(x for x in items if isinstance(x, ServerInfo))
    Activity.set_server_date(server_info.sever_date())
    name = os.path.basename(message_file)
    path_all = os.path.join(os.path.dirname(message_file), "all." + name[:-3] + "txt")
    path_tbd = os.path.join(os.path.dirname(message_file), "timebounds." + name[:-3] + "txt")
    
    acts = []
    activities =  filter(lambda x: isinstance(x, Activity), items) 
    for act in activities:
        acts.append(str(act))
    with open(path_all, "w") as out:
        for item in sorted(acts):
            out.write(item + '\n')
    
    acts = []
    activities =  filter(lambda x: isinstance(x, Activity) and (x.has_reservation() or x.has_timebound()), items)
    for act in activities:
        acts.append(str(act))
    with open(path_tbd, "w") as out:
        for item in sorted(acts):
            out.write(item + '\n')
                     
def report_transition_matrix(message_file):
    items = parse_messagefile(message_file, [Uebort, Uebaddr])
    for item in items:
        print(item)
    
def show_sub_producers(message_file):
    """a relevant sub producer produces a material which exists as a demand
       the producing part process is not the head part process
    """
    items = parse_messagefile(message_file, [PartProcess, MaterialCst, ])
    materials = filter(lambda x: isinstance(x, MaterialCst), items)
    partprocs = filter(lambda x: isinstance(x, PartProcess), items)
    demands = set()
    for mat in materials:
        #print(mat)
        if mat.quantity() > 0:
            demands.add(mat.material_key())
    
    for pp in partprocs:
        if not pp.is_head() and pp.free_quantity() > 0 and pp.material_key() in demands:
            qty = ('%f' % pp.free_quantity()).rstrip('0').rstrip('.')
            print("%s material=%s free_quantity=%s" % (pp, pp.material_key(), qty))
    return 0

def show_proc_with_fixed_acts(message_file):
    activities = parse_messagefile(message_file, [Activity,])
    fixed_acts = filter(lambda x: x.is_frozen(), activities)
    procs = set()
    for act in fixed_acts:
        procs.add(act.proc_id())
    for pid in procs:
        print(pid)

def show_resources(message_file):
    items = parse_messagefile(message_file, [Resource,])
    item_dict = {}
    for item in items:
        item_dict[item.id()] = item
    for key in sorted(item_dict.keys()):
        print(item_dict[key])
 
def pirlo_print_proc(proc):
    print('\t%s' % proc)
    res_ids = ['10-001', '10-002', '20-001', '20-002']
    for res_cst in proc.res_csts(): # filter(lambda x: x.res_id() in res_ids, proc.res_csts()):
        print('\t\t%s' % res_cst)
 
def pirlo_rename_info(processes):
    tafel_procs = filter(lambda x: x.material().find("820")==0 or x.material().find("822")==0, processes)
    mat2procs = {}
    cnt = 0
    for proc in tafel_procs:
        material = proc.material()
        mat2procs.setdefault(material, [])
        mat2procs[material].append(proc)
        cnt += 1
    for material in mat2procs:
        print("material=%s #procs=%d" % (material, len(mat2procs[material])))
        for proc in mat2procs[material]:
            pirlo_print_proc(proc)
    print("#procs=%d #tafel-procs=%d #tafel-ids=%d" % (len(processes), cnt, len(mat2procs)))
    rename_info = {}
    if 0:
        for idx_mat, material in enumerate(mat2procs):
            mat = "TAF%03d" % idx_mat
            for idx_proc, proc in enumerate(mat2procs[material]):
                id_proc = proc.proc_id()
                dst = "%s%s_%d" % (id_proc[:3], mat, idx_proc)
                rename_info[id_proc] = dst
    return rename_info
    
def pirlo_do_rename(rename_info, message_file):
    out_file = message_file.replace(".dat", ".renamed.dat")
    out = open(out_file, "w")
    for line in open(message_file):
        handled = False
        for key, dst in rename_info.items():
            if line.find(key) != -1:
                out.write(line.replace(key, dst))
                handled = True
                break
        if not handled:
            out.write(line)
    out.close()

def show_pool_selections(message_file):
    items = parse_messagefile(message_file, [MbActivity, PoolSelection,])
    pool_selections = filter(lambda x: isinstance(x, PoolSelection), items)
    act2pool = {}
    for selection in pool_selections:
        act2pool.setdefault(selection.ident_act(), []).append(selection)

    activities = filter(lambda x: isinstance(x, MbActivity), items)
    for act in activities:
        id = act.ident_act()
        if id in act2pool:
            print(act)
            for sel in act2pool[id]:
                msg = str(sel)
                print("\t%s" % msg[msg.find(' ')+1:])
            print()
        #sys.exit(0)

def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('message_file', metavar='message_file', help='input message file')
    parser.add_argument('-ts', '--to_sonic', metavar='string', # or stare_false
                      dest="to_sonic", default='', # negative store value
                      help="to_sonic file")
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
    msg_file = args.message_file
 
 
    #check_altsres(msg_file)

    if 1:
        show_pool_selections(msg_file)
        return

    if 0:
        show_proc_with_fixed_acts(msg_file)
        return
    
    if 0:
        show_resources(args.message_file)
        return 0
    
    if 0: # stadler timebounds
        report_timebounds(msg_file)
        return 0
    
    if 0:
        show_sub_producers(msg_file)
        return 0
    
    if 0:
        report_transition_matrix(msg_file)
        return 0
    
    if 0:
        report_timebounds(msg_file)
        return 0
        # show material reservations
        items = parse_messagefile(args.message_file, [Activity, ServerInfo])
        server_info =  next(x for x in items if isinstance(x, ServerInfo))
        Activity.set_server_date(server_info.sever_date())
        activities =  filter(lambda x: isinstance(x, Activity) and x.has_reservation(), items) # and x.has_reservation()
        for act in activities:
            print(act)
        return 0
 
    if 0:
        for item in parse_messagefile(msg_file, [ResReserved,]):
            print(item)
        return 0

    items = parse_messagefile(args.message_file, [PartProcess, Activity, Edge, ResourceCst, ServerInfo])
    procs = build_procs(items)
    
    if 1:
        info = pirlo_rename_info(procs.values())
        for src, dst in info.items():
            print("%s -> %s" % (src, dst))
        #pirlo_do_rename(info, args.message_file)
        return

    if args.to_sonic:
        sched_trigger = parse_sched_trigger(args.to_sonic)
        cluster = get_cluster(sched_trigger, '4882997')
        activities =  filter(lambda x: isinstance(x, Activity), items)
        show_sched_trigger(cluster, activities)
        return 0

    
    if 0:
        show_forein_acts(items)
        sys.exit(0)
    
    if 1:
        show_paths(procs)
        return 1
        
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
    
    

