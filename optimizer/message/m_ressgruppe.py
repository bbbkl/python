# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: m_ressgruppe.py
#
# description
"""\n\n
    MRessGruppe class
"""

from message.baseitem import BaseItem

class MRessGruppe(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)
    
    def ressgruppe(self):
        """get ressgruppe"""
        return self._tokens[0]
        
    def adressnr(self):
        """get adressnr"""
        return self._tokens[1]

    @classmethod        
    def commands(cls):
        return ['DEF_ERPCommandcreate_M_RessGruppe_', ]
    
    def token_descriptions(self):
        return ['RessGruppe', 'AdressNr']
