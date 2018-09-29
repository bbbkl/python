# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: m_uebort.py
#
# description
"""\n\n
    delete xy commands
"""

from message.baseitem import BaseItem
#from to_string import ToString

class DeleteProcessRueckNr(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def verbose_tokens(self):
        """possibility to enrich some cryptic values with their human readable description"""
        tokens = list(self._tokens)
        return tokens

    @classmethod        
    def commands(cls):
        return ['DEF_ERPCommanddeleteProcessRueckNr', ]
    
    def token_descriptions(self):
        return ['area', 'key']


class DeleteStaProcessRueckNr(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def verbose_tokens(self):
        """possibility to enrich some cryptic values with their human readable description"""
        tokens = list(self._tokens)
        return tokens

    @classmethod        
    def commands(cls):
        return ['DEF_ERPCommanddeleteStaProcRueckNr', ]
    
    def token_descriptions(self):
        return ['area', 'key']
    
    
class DeleteStackProcess(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def verbose_tokens(self):
        """possibility to enrich some cryptic values with their human readable description"""
        tokens = list(self._tokens)
        return tokens

    @classmethod        
    def commands(cls):
        return ['DEF_ERPCommanddeleteStackProcess__', ]
    
    def token_descriptions(self):
        return ['key', 'temp']    
    
    

class DeleteProcess(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def verbose_tokens(self):
        """possibility to enrich some cryptic values with their human readable description"""
        tokens = list(self._tokens)
        return tokens

    @classmethod        
    def commands(cls):
        return ['DEF_ERPCommanddeleteProcess_______', ]
    
    def token_descriptions(self):
        return ['key', 'idProcess']    
    
    