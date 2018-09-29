# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: process_template.py
#
# description
"""\n\n
    process template for setup matrix
"""

import sys
import os.path
from setup_matrix.setup_util import test_encoding

VERSION = '0.1'

class TrBase:
    def __init__(self, tokens):
        self._tokens = tokens.split('\t')[1:]
        self._tokens[-1] = self._tokens[-1][:-1]
        
    def __str__(self):
        tokens = [str(x) for x in self._tokens]
        return  '3\t%s\n2\t%s\n' % ('\t'.join(tokens), self.cmd())
    def set_process_id(self, val):
        self._tokens[1] = val
    def token(self, n):
        return self._tokens[n]

class TrProcess(TrBase):
    def __init__(self, tokens):
        TrBase.__init__(self, tokens)
    @classmethod
    def cmd(cls):
        return 370
        
    def set_partproc_id(self, val):
        self._tokens[2] = str(val)
    def set_duedate(self, duedate):
        self._tokens[8] = duedate     
    def set_quantity(self, val):
        self._tokens[6] = val # prod
        self._tokens[17] = val # free
        self._tokens[23] = val # total
    def set_priority(self, val):
        self._tokens[10] = str(val).replace('.', ',')
        
    
class TrAct(TrBase):
    def __init__(self, tokens):
        TrBase.__init__(self, tokens)
        self._res_csts = []
        self._prec_csts_to = []
        self._prec_csts_from = []
    @classmethod
    def cmd(cls):
        return 365
    def __str__(self):
        stream = ""
        for res_cst in self._res_csts:
            stream += str(res_cst)
        stream += TrBase.__str__(self)
        for prec_cst in self._prec_csts_to:
            stream += str(prec_cst)
        return stream
    
    @classmethod
    def to_seconds(cls, time_str):
        hour, minute = time_str.split(':')
        return 60 * (int(hour) * 60 + int(minute))
    
    def set_quantity(self, val):
        self._tokens[33] = val # total lot size
        self._tokens[35] = 60 * int(val)
    
    def set_start(self, date, time):
        self._tokens[14] = date
        self._tokens[20] = TrAct.to_seconds(time)
    def set_end(self, date, time):
        self._tokens[15] = date
        self._tokens[21] = TrAct.to_seconds(time)
    def set_fixed(self, val):
        self._tokens[16] = "1" if val else "0"
     
    def partproc_id(self):
        return int(self._tokens[2])
    def set_partproc_id(self, val):
        self._tokens[2] = str(val)    
    def ident_act(self):
        return int(self._tokens[5])
    def set_ident_act(self, val):
        self._tokens[5] = int(val)
    def set_activity_class(self, val):
        self._tokens[31] = val
    def set_lotsize(self, val):
        self._tokens[33] = val
        self._tokens[35] = 60 * val
        
    def add_res_cst(self, res_cst):
        self._res_csts.append(res_cst)
    def res_csts(self):
        return self._res_csts
    def add_prec_to(self, prec_cst):
        self._prec_csts_to.append(prec_cst)
    def add_prec_from(self, prec_cst):
        self._prec_csts_from.append(prec_cst)
    def prec_csts_to(self):
        return self._prec_csts_to
    def prec_csts_from(self):
        return self._prec_csts_from

class TrResCst(TrBase):
    def __init__(self, tokens):
        TrBase.__init__(self, tokens)      
    @classmethod
    def cmd(cls):
        return 350
    
    def set_partproc_id(self, val):
        self._tokens[2] = val
    def ident_act(self):
        return int(self._tokens[7])
    def set_ident_act(self, val):
        self._tokens[7] = val
    def set_resource(self, val):
        self._tokens[6] = val


class TrPrecedenceCst(TrBase):
    def __init__(self, tokens):
        TrBase.__init__(self, tokens)    
    @classmethod
    def cmd(cls):
        return 360
    
    def ident_act_from(self):
        return int(self._tokens[3])
    def ident_act_to(self):
        return int(self._tokens[5])
    def partproc_id_from(self):
        return int(self._tokens[2])
    def partproc_id_to(self):
        return int(self._tokens[4])
      
    def set_from(self, partproc_id, ident_act):
        self._tokens[2] = partproc_id
        self._tokens[3] = ident_act
    def set_to(self, partproc_id, ident_act):
        self._tokens[4] = partproc_id
        self._tokens[5] = ident_act

class ProcessTemplate:
    _ident_act = 77000
    _ppid = 33000
    _prio = 1000
    _pid = 0;
    
    def __init__(self, proc, acts, res_csts, precedence_csts):
        self._proc = proc
        self._acts = acts
        for item in res_csts:
            self.assign_res_cst(item)
        for item in precedence_csts:
            self.assign_prec_cst(item)
            
    @classmethod
    def getnext_ident_act(cls):
        ProcessTemplate._ppid += 1
        return ProcessTemplate._ppid -1
    
    @classmethod
    def getnext_prio(cls):
        ProcessTemplate._prio -= 1
        return (ProcessTemplate._prio)
    
    @classmethod
    def getnext_process_id(cls):
        ProcessTemplate._pid += 1
        return "RUESTOPTI_%03d" % (ProcessTemplate._pid -1)
    
    @classmethod
    def getnext_partproc_id(cls):
        ProcessTemplate._ident_act += 1
        return ProcessTemplate._ident_act -1
            
    def fix_activity(self, idx_act, date_start, time_start, date_end, time_end):
        act = self._acts[idx_act]
        act.set_fixed(True)
        act.set_start(date_start, time_start)
        act.set_end(date_end, time_end)
            
    def assign_res_cst(self, res_cst):
        act_id = res_cst.ident_act()
        for act in self._acts:
            if act.ident_act()==act_id:
                act.add_res_cst(res_cst)
                break
            
    def assign_prec_cst(self, prec_cst):
        act_id_to = prec_cst.ident_act_to()
        act_id_from = prec_cst.ident_act_from()
        ppid_to = prec_cst.partproc_id_to()
        ppid_from = prec_cst.partproc_id_from()
        for act in self._acts:
            id_act = act.ident_act()
            id_pp = act.partproc_id()
            if id_act==act_id_to and id_pp==ppid_to:
                act.add_prec_to(prec_cst)
            if id_act==act_id_from and id_pp==ppid_from:
                act.add_prec_from(prec_cst)
            
    def reassign_all(self):
        self.reassign_process_id()
        self.reassign_priority()
        self.reassign_partproc_id()
        self.reassign_ident_act()
            
    def reassign_process_id(self):
        self.set_process_id(ProcessTemplate.getnext_process_id())
            
    def reassign_ident_act(self):
        for act in self._acts:
            ident_act_new = ProcessTemplate.getnext_ident_act()
            ProcessTemplate.replace_in_act(act, act.partproc_id(), ident_act_new)
    
    def reassign_priority(self):
        self._proc.set_priority(ProcessTemplate.getnext_prio())
        
    def reassign_partproc_id(self):
        self.set_partproc_id(ProcessTemplate.getnext_partproc_id())
            
    @classmethod    
    def replace_in_act(cls, act, ppid_new, ident_act_new):
        ppid_old = act.partproc_id()
        ident_act_old = act.ident_act()
        act.set_partproc_id(ppid_new)
        act.set_ident_act(ident_act_new)
        for cst in act.prec_csts_to():
            if cst.ident_act_to() == ident_act_old and cst.partproc_id_to() == ppid_old:
                cst.set_to(ppid_new, ident_act_new)
            if cst.ident_act_from() == ident_act_old and cst.partproc_id_from() == ppid_old:
                cst.set_from(ppid_new, ident_act_new)
        for cst in act.prec_csts_from():
            if cst.ident_act_to() == ident_act_old and cst.partproc_id_to() == ppid_old:
                cst.set_to(ppid_new, ident_act_new)
            if cst.ident_act_from() == ident_act_old and cst.partproc_id_from() == ppid_old:
                cst.set_from(ppid_new, ident_act_new)
        for cst in act.res_csts():
            cst.set_partproc_id(ppid_new)
            cst.set_ident_act(ident_act_new)
            
    def __str__(self):
        stream = str(self._proc)
        for act in self._acts:
            stream += str(act)
        return stream
    
    def set_quantity(self, val):
        self._proc.set_quantity(val)
        for act in self._acts:
            act.set_quantity(val)
        
    def set_process_id(self, val):
        self._proc.set_process_id(val)
        for act in self._acts:
            for res_cst in act.res_csts():
                res_cst.set_process_id(val)
            for cst in act.prec_csts_from():
                cst.set_process_id(val)
            act.set_process_id(val)
    
    def set_partproc_id(self, val):
        self._proc.set_partproc_id(val)
        for act in self._acts:
            ProcessTemplate.replace_in_act(act, val, act.ident_act())
        
    def set_duedate(self, val):
        self._proc.set_duedate(val)
        
    def set_activity_class(self, val):
        for act in self._acts:
            act.set_activity_class(val)
        
def get_script_path():
        return os.path.dirname(os.path.realpath(sys.argv[0]))

def parse_process_template(which_template):
    template = "setup_matrix/process_template_%s.txt" % which_template
    fn = os.path.join(get_script_path(), template)
    encoding_id = test_encoding(fn)
    
    classes = [TrProcess, TrAct, TrResCst, TrPrecedenceCst]
    objects = {}
    for item in classes:
        objects.setdefault(item, [])
    
    dataline = None
    for line in open(fn, encoding=encoding_id):
        object_found = False
        for item in classes:
            if line.find('2\t%d' % item.cmd())!=-1:
                objects[item].append(item(dataline))
                dataline = None
                object_found = True
                break
        dataline = None if object_found else line 
            
    proc = ProcessTemplate(objects[TrProcess][0], 
                           objects[TrAct], 
                           objects[TrResCst], 
                           objects[TrPrecedenceCst])
    
    
    return proc

