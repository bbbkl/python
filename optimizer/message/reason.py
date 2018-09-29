# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: reason.py
#
# description
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
