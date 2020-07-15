# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: reason.py
#
# description
from _ctypes import Structure
"""\n\n
    Reason info classes (send from optimizer to erp)
"""

from message.baseitem import BaseItem
from to_string import ToString

class ReasonMaterial(BaseItem):
    """One material reason"""
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def opt_number(self):
        """get optimization number"""
        return self._tokens[0]

    def is_ctp(self):
        """is a ctp yes/no"""
        return self._tokens[1]

    def proc_id(self):
        """get proc id"""
        return self._tokens[3]

    def part(self):
        """get material"""
        return self._tokens[5]

    def is_combi(self):
        return 0 if self._tokens[15] == "0" else 1

    def headline_ids(self):
        """get headline for explained mode"""
        return "%s %s %s %s %s" % (self.opt_number(), self.is_ctp(), self.proc_id(), self.part(), self.is_combi())

    def verbose_tokens(self):
        """possibility to enrich some cryptic values with their human readable description"""
        tokens = list(self._tokens)
        self.verbose_token(2, ToString.determination_type, tokens) # determination_type
        return tokens

    @classmethod
    def commands(cls):
        return ['DEF_APSCommandcreate_ReasonMat____', 'DEF_APSCommandcreate_ReasonMatResM']

    def token_descriptions(self):
        return ['OptNum', 'is_ctp', 'determination_type', 'Process', 'ActPartproc',
                'part', 'ArtVariante', 'lot', 'cro', 'date', 'Zeit',
                'ActPos', 'ActSplitNr', 'needed_amount', 'Missing_amount',
                'combi_reason_id', 'Partproc', 'Tardiness', 'ActTardiness',
                'PartprocIsTemp', 'ActPartprocIsTemp', 'reservation', 'used_replenishment_time']


class ReasonResource(BaseItem):
    """One resource reason"""
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def opt_number(self):
        """get optimization number"""
        return self._tokens[0]

    def is_ctp(self):
        """is a ctp yes/no"""
        return self._tokens[1]

    def proc_id(self):
        """get proc id"""
        return self._tokens[3]

    def headline_ids(self):
        """get headline for explained mode"""
        return "%s %s %s" % (self.opt_number(), self.is_ctp(), self.proc_id())

    def verbose_tokens(self):
        """possibility to enrich some cryptic values with their human readable description"""
        tokens = list(self._tokens)
        self.verbose_token(2, ToString.determination_type, tokens) # determination_type
        return tokens

    @classmethod
    def commands(cls):
        return ['DEF_APSCommandcreate_ReasonRes____', 'DEF_APSCommandcreate_ReasonMatResR']

    def token_descriptions(self):
        return ['OptNum', 'is_ctp', 'determination_type', 'Process', 'ActPartproc',
                'res_kind', 'ResId', 'ActPos', 'ActSplitNr', 'EarliestNonDelayStartDate',
                'EarliestNonDelayTime', 'LatestNonDelayEndDate', 'LatestNonDelayEndTime',
                'combi_reason_id', 'Partproc', 'Tardiness', 'ActTardiness', 'Fully_verified',
                'PartprocIsTemp', 'ActPartprocIsTemp']


class ReasonResRes(BaseItem):
    """One combi resource reason"""
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def opt_number(self):
        """get optimization number"""
        return self._tokens[0]

    def is_ctp(self):
        """is a ctp yes/no"""
        return self._tokens[1]

    def proc_id(self):
        """get proc id"""
        return self._tokens[3]

    def headline_ids(self):
        """get headline for explained mode"""
        return "%s %s %s" % (self.opt_number(), self.is_ctp(), self.proc_id())

    def verbose_tokens(self):
        """possibility to enrich some cryptic values with their human readable description"""
        tokens = list(self._tokens)
        self.verbose_token(2, ToString.determination_type, tokens) # determination_type
        return tokens

    @classmethod
    def commands(cls):
        return ['DEF_APSCommandcreate_ReasonResRes_']

    def token_descriptions(self):
        return ['OptNum', 'is_ctp', 'determination_type', 'Process', 'ActPartproc',
                'res_kind', 'ResId', 'ActPos', 'ActSplitNr', 'EarliestNonDelayStartDate',
                'EarliestNonDelayTime', 'LatestNonDelayEndDate', 'LatestNonDelayEndTime',
                'capacity_requirement', 'combi_reason_id', 'is_leading_resource', 'Partproc',
                'Tardiness', 'ActTardiness', 'Fully_verified', 
                'PartprocIsTemp', 'ActPartprocIsTemp']


class ReasonTimebound(BaseItem):
    """One timebound reason"""
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def opt_number(self):
        """get optimization number"""
        return self._tokens[0]

    def is_ctp(self):
        """is a ctp yes/no"""
        return self._tokens[1]

    def proc_id(self):
        """get proc id"""
        return self._tokens[3]

    def headline_ids(self):
        """get headline for explained mode"""
        return "%s %s %s" % (self.opt_number(), self.is_ctp(), self.proc_id())

    def verbose_tokens(self):
        """possibility to enrich some cryptic values with their human readable description"""
        tokens = list(self._tokens)
        self.verbose_token(12, ToString.timebound_originator, tokens) # originator
        return tokens

    @classmethod
    def commands(cls):
        return ['DEF_APSCommandcreate_ReasonTimebnd']

    def token_descriptions(self):
        return ['OptNum', 'is_ctp', 'determination_type', 'Process', 'ActPartproc',
                'ActPos', 'ActSplitNr', 'TimeboundDate', 'TimeboundTime',
                'EarliestEndWithTBDate (unused)', 'EarliestEndWithTBTime (unused)',
                'Tardiness', 'Originator', 'Details', 'Partproc', 'ActTardiness',
                'PartprocIsTemp', 'ActPartprocIsTemp']


class ReasonAdmin(BaseItem):
    """One admin reason"""
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def opt_number(self):
        """get optimization number"""
        return self._tokens[0]

    def is_ctp(self):
        """is a ctp yes/no"""
        return self._tokens[1]

    def proc_id(self):
        """get proc id"""
        return self._tokens[3]

    def headline_ids(self):
        """get headline for explained mode"""
        return "%s %s %s" % (self.opt_number(), self.is_ctp(), self.proc_id())

    def verbose_tokens(self):
        """possibility to enrich some cryptic values with their human readable description"""
        tokens = list(self._tokens)
        self.verbose_token(4, ToString.optimization_type, tokens) # optimization_type
        self.verbose_token(5, ToString.last_opt_target, tokens) # opt_target
        return tokens

    @classmethod
    def commands(cls):
        return ['DEF_APSCommandcreate_ReasonAdmin__']

    def token_descriptions(self):
        return ['OptNum', 'is_ctp', 'determination_type', 'Process',
                'optimization_type', 'opt_target',
                'has_reasons', 'DueDate', 'DueDateTime', 'Partproc',
                'PartprocIsTemp', 'is_tardy', 'calc_reasons']


class ReasonStructure(BaseItem):
    """One structure reason"""
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def opt_number(self):
        """get optimization number"""
        return self._tokens[0]

    def is_ctp(self):
        """is a ctp yes/no"""
        return self._tokens[1]

    def proc_id(self):
        """get proc id"""
        return self._tokens[3]

    def headline_ids(self):
        """get headline for explained mode"""
        return "%s %s %s" % (self.opt_number(), self.is_ctp(), self.proc_id())

    def verbose_tokens(self):
        """possibility to enrich some cryptic values with their human readable description"""
        tokens = list(self._tokens)
        self.verbose_token(12, ToString.structure_reason_subtype, tokens) # reason subtype
        return tokens

    @classmethod
    def commands(cls):
        return ['DEF_APSCommandcreate_ReasonStruc__']

    def token_descriptions(self):
        return ['OptNum', 'is_ctp', 'determination_type',
                'Process', 'Partproc (unused)',
                'earliestStartDate', 'earliestStartTime',
                'earliestEndDate', 'earliestEndTime', 'tardiness', 'Partproc',
                'PartprocIsTemp', 'ReasonSubtype']


# new 7.1 reasons commands
class ReasonHead(BaseItem):
    """One reason head"""
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def partproc(self):
        """get part proc id"""
        return self._tokens[1]

    def is_cluster(self):
        """1 = cluster"""
        return self._tokens[2]

    def is_ctp(self):
        """is a ctp yes/no"""
        return self._tokens[3]

    def headline_ids(self):
        """get headline for explained mode"""
        return "%s %s %s" % (self.is_cluster(), self.is_ctp(), self.partproc())

    def verbose_tokens(self):
        """possibility to enrich some cryptic values with their human readable description"""
        tokens = list(self._tokens)
        self.verbose_token(0, ToString.scheduling_obj_type, tokens)
        self.verbose_token(8, ToString.reasoning_state, tokens)
        return tokens

    @classmethod
    def commands(cls):
        return ['DEF_APSCommandcreate_ReasonHead___']

    def token_descriptions(self):
        return ['head_obj_type', 'part_process', 'is_cluster_reason', 'is_ctp',
                'due_date', 'due_time',
                'optimization_type', 'opt_target', 'reasoning_state', 'is_cluster_reason_head']

class Reason(BaseItem):
    """One sub reason which belongs to a reason head"""
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def is_ctp(self):
        """is a ctp yes/no"""
        return self._tokens[3]

    def partproc(self):
        """get part proc id"""
        return self._tokens[1]

    def transmission_id(self):
        """transmission id"""
        return self._tokens[4]

    def headline_ids(self):
        """get headline for explained mode"""
        return "%s %s" % (self.transmission_id(), self.partproc())

    def reason_type(self):
        return int(self._tokens[5])

    def verbose_tokens(self):
        """possibility to enrich some cryptic values with their human readable description"""
        tokens = list(self._tokens)
        self.verbose_token(0, ToString.scheduling_obj_type, tokens)
        self.verbose_token(5, ToString.reason_type, tokens)
        return tokens

    @classmethod
    def commands(cls):
        return ['DEF_APSCommandcreate_Reason_______']

    def token_descriptions(self):
        res = ['head_obj_type', 'part_process', 'is_cluster_reason', 'is_ctp',
                'transmission_id', 'reason_type', 'tardiness', 'earliest_end_date', 'earliste_end_time']
        
        if self.reason_type() == 20: # Structure
            res.extend(['subtype',])
        elif self.reason_type() == 30: # timebound
            res.extend(['timebound_date', 'timebound_time', 'subtype', 'details'])
        elif self.reason_type() == 40: # res
            res.extend(['res_kind', 'res']) 
        elif self.reason_type() == 50: # mat
            res.extend(['part', 'art_var', 'lot', 'lot', 'reservation', 'replenishment_time'])
        elif self.reason_type() == 60: # combi mat/res
            res.extend(['part', 'art_var', 'lot', 'lot', 'reservation', 'replenishment_time',
                        'res_kind', 'res' ])
        elif self.reason_type() == 70: # combi res/res
            res.extend(['res1_kind', 'res1', 'res2_kind', 'res2'])
        else:
            res.extend(['par10', 'par11', 'par12', 'par13', 'par14', 'par15', 'par16', 'par17'])

        return res

class ReasonAct(BaseItem):
    """One reason activity which belongs to a reason"""
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def act_type(self):
        """what object this reason refers to"""
        return ToString.scheduling_obj_type(self._tokens[0])

    def ident_act(self):
        """id of act"""
        return self._tokens[1]

    def transmission_id(self):
        """transmission id"""
        return self._tokens[2]

    def headline_ids(self):
        """get headline for explained mode"""
        return "%s %s" % (self.transmission_id(), self.ident_act())

    def verbose_tokens(self):
        """possibility to enrich some cryptic values with their human readable description"""
        tokens = list(self._tokens)
        self.verbose_token(0, ToString.scheduling_obj_type, tokens)
        return tokens

    @classmethod
    def commands(cls):
        return ['DEF_APSCommandcreate_ReasonAct____']

    def token_descriptions(self):
        return ['act_type', 'ident_act', 'transmission_id', 'tardiness_act',
                'earliest_start_date', 'earliest_start_time',
                'latest_non_delay_end_date', 'latest_non_delay_end_time',
                'demand_date', 'demand_time',
                'missing_amount', 'needed_amount', 'resource_reference']
