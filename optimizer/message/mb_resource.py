# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: mb_resource.py
#
# description
"""\n\n
    MbResource
"""

from message.baseitem import BaseItem
from to_string import ToString

class MbResource(BaseItem):
    """One MbResource"""
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def partproc_id(self):
        """get partproc id"""
        return self._tokens[4]

    def ident_akt(self):
        """get activity id"""
        return self._tokens[0]

    def res_art(self):
        """get resource kind"""
        return self._tokens[1]

    def resource(self):
        """get resource id"""
        return self._tokens[2]

    def headline_ids(self):
        """get headline for explained mode"""
        return "%s %s %s" % (self.partproc_id(), self.ident_akt(), self.resource())

    @classmethod
    def commands(cls):
        return ['DEF_APSCommandcreate_MB_Ressource_', ]

    def token_descriptions(self):
        return ['ident_act', 'res_kind', 'res', 'res_pos', 'part_process', 'process_area']

  
class MResourceKombination(BaseItem):
    """One MbResource"""
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def res_art1(self):
        """res art machine"""
        return self._tokens[0]

    def res1(self):
        """res machine"""
        return self._tokens[1]

    def res_art2(self):
        """res art tool"""
        return self._tokens[2]

    def res2(self):
        """res tool"""
        return self._tokens[3]

    def verbose_tokens(self):
        """possibility to enrich some cryptic values with their human readable description"""
        tokens = list(self._tokens)
        self.verbose_token(0, ToString.resource_type, tokens) # res_art1
        self.verbose_token(2, ToString.resource_type, tokens) # res_art2
        return tokens

    def headline_ids(self):
        """get headline for explained mode"""
        return "%s %s %s %s" % (self.res_art1(), self.res1(), self.res_art2(), self.res1())

    @classmethod
    def commands(cls):
        return ['DEF_ERPCommandcreate_M_RessKombina', ]

    def token_descriptions(self):
        return [ 'res_type_machine', 'res_machine', 'res_type_tool', 'res_tool' ]

class PoolSelection(BaseItem):
    """One pool selection"""
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def ident_akt(self):
        """get activity id"""
        return self._tokens[0]

    def resource(self):
        """get resource id"""
        return self._tokens[4]

    def time_range(self):
        """return from - to but only dates"""
        idx = 5
        return "%s - %s" % (self._tokens[idx], self._tokens[idx+2])

    def headline_ids(self):
        """get headline for explained mode"""
        return "%s %s %s" % (self.ident_akt(), self.resource(), self.time_range())

    @classmethod
    def commands(cls):
        return ['DEF_APSCommandcreate_PoolSelection', ]

    def token_descriptions(self):
        return ['ident_act', 'is_temporary', 'pool_res_pos', 'res_kind', 'selected_res', \
                'start_date', 'start_time', 'end_date', 'end_time']


class ResReserved(BaseItem):
    """One pool selection"""
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def ident_akt(self):
        """get activity id"""
        return self._tokens[2]

    def resource(self):
        """get resource id"""
        return self._tokens[5]

    def time_range(self):
        """return from - to but only dates"""
        idx = 5
        return "%s - %s" % (self._tokens[idx], self._tokens[idx+2])

    def headline_ids(self):
        """get headline for explained mode"""
        return "%s %s %s" % (self.ident_akt(), self.resource(), self.time_range())

    @classmethod
    def commands(cls):
        return ['DEF_ERPCommandcreate_ResReserved__', ]

    def token_descriptions(self):
        return ['ident_act', 'is_temporary', 'res_kind', 'res',      
                'start_date', 'start_time', 'end_date', 'end_time']
    
