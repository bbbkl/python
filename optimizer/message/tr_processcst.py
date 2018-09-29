# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: tr_processcst.py
#
# description
"""\n\n
    TrProcessCst class
"""

from message.baseitem import BaseItem

class TrProcessCst(BaseItem):
    """One TrProcessCst"""
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)
        self._zeitmengeneinheit_dict = {}
        
    def __str__(self):
        return "trprocesscst"
        
    def process_id_from(self):
        """get process id from"""
        return self._tokens[1]
    
    def process_id_to(self):
        """get process id to"""
        return self._tokens[3]
    
    def process_bereich_from(self):
        """get process bereich from"""
        return self._tokens[0]
    
    def process_bereich_to(self):
        """get process bereich to"""
        return self._tokens[2]
    
    def next_akt_key(self):
        """get next akt key"""
        return self._tokens[4]

    def days_delay(self):    
        """get days delay"""
        return self._tokens[5]
    
    def headline_ids(self):
        return "%s %s %s" % (self.process_id_from(), self.process_id_to(), self.next_akt_key())   
        
    @classmethod        
    def commands(cls):
        return ['DEF_ERPCommandcreate_ProcessCst___', ]
    
    def token_descriptions(self):
        return ['ProzessBereich_FROM', 'Prozess_FROM', 'ProzessBereich_TO', 'Prozess_TO', 'NextAktKey', 'DaysDelay', 'RmNr_FROM'] 