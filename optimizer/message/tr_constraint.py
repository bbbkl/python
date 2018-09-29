# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: tr_constraint.py
#
# description
"""\n\n
    TrConsraint class
"""

from message.baseitem import BaseItem
from to_string import ToString

class TrConstraint(BaseItem):
    """One TrConstraint"""
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)
        self._zeitmengeneinheit_dict = {}
        
    def __str__(self):
        return "trconstraint"
        
    def process_id(self):
        """get actitiy's process id"""
        return self._tokens[1]
    
    def process_bereich_from(self):
        """get process bereich from"""
        return self._tokens[0]
    
    def process_bereich_to(self):
        """get process bereich from"""
        if len(self._tokens)>13:
            return self._tokens[13]
        return self.process_bereich_from() 
    
    def part_process_from(self):
        """get part process from"""
        return self._tokens[2]
    
    def part_process_to(self):
        """get part process to"""
        return self._tokens[4]
    
    def ident_akt_from(self):
        """get activity id from"""
        return self._tokens[3]
    
    def ident_akt_to(self):
        """get activity id to"""
        return self._tokens[5]
    
    def transition_time(self):
        """get transition time"""
        return int(self._tokens[6])
    
    def transition_time_unit(self):
        """get transition time unit"""
        return int(self._tokens[7])
    
    def dynamic_buffer_time(self):
        """get dynamic buffer time"""
        pos = 14
        if len(self._tokens) > pos:
            return int(self._tokens[pos])
        return 0
    
    def dynamic_buffer_time_unit(self):
        """get dynamic buffer time unit"""
        pos = 15
        if len(self._tokens) > pos:
            return int(self._tokens[pos])
        return 0
    
    def aob(self):
        return int(self._tokens[8])
    
    def part_lot(self):
        return '1'==self._tokens[9]
    
    def zeitwahl(self):
        return self._tokens[10]
    
    def quantity_part_lot(self):
        return self.to_float(self._tokens[11])
    
    def quantity_part_lot_je(self):
        return int(self._tokens[12])
    
    def verbose_tokens(self):
        """possibility to enrich some cryptic values with their human readable description"""
        tokens = list(self._tokens)
        self.verbose_token(7, ToString.time_unit, tokens)
        self.verbose_token(8, ToString.aob, tokens)
        self.verbose_token(15, ToString.time_unit, tokens)
        return tokens
    
    def headline_ids(self):
        return "%s %s %s AOB_%s %s %s" % (self.process_id(), self.part_process_from(), self.ident_akt_from(), 
                             ToString.aob(self.aob()), self.part_process_to(), self.ident_akt_to())   
        
    @classmethod        
    def commands(cls):
        return ['DEF_ERPCommandcreate_Constraint___', ]
    
    def token_descriptions(self):
        if self.mode51():
            return ['process_area_from', 'process', 'part_process_from', 'ident_act_from', 
                'part_process_to', 'ident_act_to', 'transport_time',
                'transport_time_unit', 'AOB', 'Teillos', 'Zeitwahl',
                'Menge_Teillos', 'Je_Menge_Teillos', 'process_are_to']
        return ['process_area_from', 'process', 'part_process_from', 'ident_act_from', 
                'part_process_to', 'ident_act_to', 'transport_time',
                'transport_time_unit', 'AOB', 'Teillos', 'Zeitwahl',
                'Menge_Teillos', 'Je_Menge_Teillos', 'process_are_to',
                'buffer_time', 'buffer_time_unit', 'buffer_bound'] # not in 5.1