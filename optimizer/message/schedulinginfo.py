# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: schedulinginfo.py
#
# description
"""\n\n
   SchedulingInfo / SchedulingTrigger 
"""

from message.baseitem import BaseItem
from to_string import ToString

class SchedulingInfo(BaseItem):
    """One scheduling info"""
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def verbose_tokens(self):
        """possibility to enrich some cryptic values with their human readable description"""
        tokens = list(self._tokens)
        self.verbose_token(0, ToString.scheduling_obj_type, tokens) # determination_type
        return tokens

    @classmethod
    def commands(cls):
        return ['DEF_APSCommandcreate_SchedInfo____',]

    def token_descriptions(self):
        return ['objTypeCode', 'objId', 'priority', 'aps_date', 'mrp_level',
                'with_ovl', 'planning_pos', 'age', 'job_no']


class SchedulingTrigger(BaseItem):
    """One scheduling trigger"""
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def verbose_tokens(self):
        """possibility to enrich some cryptic values with their human readable description"""
        tokens = list(self._tokens)
        self.verbose_token(0, ToString.scheduling_obj_type, tokens) # demand obj_type
        self.verbose_token(3, ToString.scheduling_obj_type, tokens) # cover obj_type
        return tokens

    @classmethod
    def commands(cls):
        return ['DEF_APSCommandcreate_SchedTrigger_',]

    def token_descriptions(self):
        return ['demandObjType', 'demandId', 'demand_date',
                'coverObjType', 'coverId', 'job_no']