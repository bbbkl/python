# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: mc_charge.py
#
# description
"""\n\n
    McCharge class
"""

from message.baseitem import BaseItem

class McCharge(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)
    
    def charge(self):
        """get charge"""
        return self._tokens[0]
        
    def artikel(self):
        """get artikel"""
        return self._tokens[1]
    
    def verfallsdatum(self):
        """get verfallsdatum"""
        return self._tokens[2]

    @classmethod        
    def commands(cls):
        return ['DEF_ERPCommandcreate_MC_Charge____', ]
    
    def token_descriptions(self):
        if len(self._tokens) == 4:
            return ['lot', 'part',  'Verfallsdatum', '???']
        return ['lot', 'part',  'Verfallsdatum']
