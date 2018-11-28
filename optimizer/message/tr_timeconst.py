# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: tr_timeconst.py
#
# description
"""\n\n
    TrTimeConst = timebound constraint on an activity
"""

from message.baseitem import BaseItem
from to_string import ToString

class TrTimeConst(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    @classmethod        
    def commands(cls):
        return ['DEF_ERPCommandcreate_TimeConst____', ]
    
    def verbose_tokens(self):
        """possibility to enrich some cryptic values with their human readable description"""
        tokens = list(self._tokens)
        self.verbose_token(5, ToString.time_condition, tokens)
        return tokens   
    
    def token_descriptions(self):
        return ['process_area_head', 'process', 'part_process',
                'ident_act', 'condition_date', 'condition_type (not used, always >=)' ]

