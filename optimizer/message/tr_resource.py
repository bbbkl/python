# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: resource.py
#
# description
"""\n\n
    TrResource class
"""

from message.baseitem import BaseItem
from to_string import ToString

class TrResource(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)
        self._m_resources = []
        self._m_res_alt_group = []
        
    def process_id(self):
        return self._tokens[1]
    
    def prozessbereich(self):
        return self._tokens[0]
        
    def teilprozess(self):
        return self._tokens[2]
    
    def akt_pos(self):
        return self._tokens[3]
    
    def res_pos(self):
        return self._tokens[4]
    
    def ident_akt(self):
        return self._tokens[7]
    
    def activity_key(self):
        return "%s_%s_%s_%s" % (self.prozessbereich(), self.process_id(), self.teilprozess(), self.ident_akt())
    
    def intensity(self):
        return self.to_float(self._tokens[8])
    
    def use_alt_group(self):
        return self._tokens[9] == '1'
    
    def is_basis_resource(self):
        return self._tokens[10] == '1'
    
    def res_art(self):
        return int(self._tokens[5])
        
    def resource(self):
        return self._tokens[6]
    
    def m_resource(self):
        if len(self._m_resources):
            return self._m_resources[0]
        return None
    
    def get_resource(self):
        if self.use_alt_group():
            if len(self._m_res_alt_group):
                return self._m_res_alt_group[0]
        return self.m_resource()
    
    def set_m_resources(self, m_resources):
        self._m_resources = m_resources
        
    def set_alt_res_group(self, group):
        self._m_res_alt_group = group

    def res_key(self):
        return self.make_key(self.res_art(), self.resource())
              
    def get_alt_group_key(self):
        return self.res_key()
    
    def verbose_tokens(self):
        """possibility to enrich some cryptic values with their human readable description"""
        tokens = list(self._tokens)
        self.verbose_token(5, ToString.resource_type, tokens)
        return tokens   
      
    def headline_ids(self):
        return "%s %s %s %s" % (self.process_id(), self.teilprozess(), self.ident_akt(), self.resource())      
      
    @classmethod        
    def commands(cls):
        return ['DEF_ERPCommandcreate_Resource_____', ]
    
    def token_descriptions(self):
        return ['process_area', 'process', 'part_process', 'act_pos', 'res_pos',
                'res_kind', 'res', 'ident_act', 'intensity', 'alt_group', 'base_res',
                'selected_res', 'overload_used', 'multiple_choice']
