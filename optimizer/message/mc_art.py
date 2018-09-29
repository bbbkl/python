# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: mc_art.py
#
# description
"""\n\n
    McArt class
"""

from message.baseitem import BaseItem

class McArt(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)
    
    def chargenart(self):
        """get charge"""
        return self._tokens[0]
        
    def fertigungsmix(self):
        """get artikel"""
        return self._tokens[1]
    
    def verfallsdatum(self):
        """get verfallsdatum"""
        return self._tokens[2]

    @classmethod        
    def commands(cls):
        return ['DEF_ERPCommandcreate_MC_Art_______', ]
    
    def token_descriptions(self):
        return ['Chargenart', 'Fertigungsmix',  'Verfallsdatum']
