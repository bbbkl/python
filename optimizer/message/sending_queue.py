# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: sending_queue.py
#
# description
"""\n\n
    Miscellaneous commands for optimizer from sending queue 
"""

from message.baseitem import BaseItem
#from to_string import ToString

class RollbackSimulationMode(BaseItem):
    """delete simulation mode"""    
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)
        
    #def headline_ids(self):
    #    """get headline for explained mode"""
    #    return "%s" % self._command.text()
        
    @classmethod
    def commands(cls):
        return ['DEF_ERPCommandRollbackSimulation__', ]


    def token_descriptions(self):
        return ['unknown_field', ] 

class DelSimulationMode(BaseItem):
    """delete simulation mode"""    
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)
        
    #def headline_ids(self):
    #    """get headline for explained mode"""
    #    return "%s" % self._command.text()
        
    @classmethod
    def commands(cls):
        return ['DEF_ERPCommandDelSimulationMode___', ]


    def token_descriptions(self):
        return ['SimModeOwner', ] 
    