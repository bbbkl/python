# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: mc_lager.py
#
# description
"""\n\n
    McLager class
"""

from message.baseitem import BaseItem

class McLager(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)
        
    def artikel(self):
        """get artikel"""
        return self._tokens[0]
    
    def charge(self):
        """get charge"""
        return self._tokens[1]
    
    def lagerort(self):
        """get lagerort"""
        return self._tokens[2]
    
    def bestand(self):
        """get lagerort"""
        return self.to_float(self._tokens[3])
    
    def resbestand(self):
        """get lagerort"""
        return self.to_float(self._tokens[4])
    
    def mrp_area(self):
        """get lagerort"""
        return self._tokens[5]

    @classmethod        
    def commands(cls):
        return ['DEF_ERPCommandcreate_MC_Lager_____', ]
    
    def token_descriptions(self):
        return ['part', 'lot', 'Lagerort', 'Bestand', 'ResBestand', 'mrp_area',
                'reservation']
