# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: mb_ressoverl.py
#
# description
"""\n\n
    MbResOverl / MaSelUebRess class
"""

from message.baseitem import BaseItem

class MbResOverl(BaseItem):
    """One TrActivity"""
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def partproc_id(self):
        """get partproc id"""
        return self._tokens[1]

    def ident_akt(self):
        """get activity id"""
        return self._tokens[0]

    def headline_ids(self):
        """get headline for explained mode"""
        return "%s %s" % (self.partproc_id(), self.ident_akt())

    @classmethod
    def commands(cls):
        return ['DEF_APSCommandcreate_MB_RessOverl_', ]

    def token_descriptions(self):
        return ['ident_act', 'pos', 'with_overload', 'part_process', 'process_area']
    

class MaSelUebRess(BaseItem):
    """One overlaod information item (for 5.2)"""
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)
        
    @classmethod
    def commands(cls):
        return ['DEF_APSCommandcreate_MA_SelUebRess', ]

    def token_descriptions(self):
        return ['process_area', 'process', 'part_process', 'ident_act', 'pos', 
                'res_kind', 'res', 'res_pos', 'start_date', 'start_time',
                'end_data', 'end_time', 'local_ovl_val' ]