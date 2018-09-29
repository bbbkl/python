# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: m_uebort.py
#
# description
"""\n\n
    miscellaneous commands
"""

from message.baseitem import BaseItem
#from to_string import ToString

"""
'DEF_ERPCommandcreate_P_ZeitMngEinh',
            '',
            '',
            '',
            '',
            '',
            
            ''
"""

class CreateContTimePoint(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def verbose_tokens(self):
        """possibility to enrich some cryptic values with their human readable description"""
        tokens = list(self._tokens)
        return tokens

    @classmethod        
    def commands(cls):
        return ['DEF_ERPCommandcreate_ContTimePoint', ]
    
    def token_descriptions(self):
        return ['process_area', 'process', 'part_process', 'ident_act', 'tp_date', 'tp_time',
                'continous_sequence', 'continous_prod_act', 'continous_demand_act']
     
     
     
class CreateZeitMengenEinheit(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def verbose_tokens(self):
        """possibility to enrich some cryptic values with their human readable description"""
        tokens = list(self._tokens)
        return tokens

    @classmethod        
    def commands(cls):
        return ['DEF_ERPCommandcreate_P_ZeitMngEinh', ]
    
    def token_descriptions(self):
        return ['zeit_mengen_einheit', 'factor']        
        
class SetDatabaseTime(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def verbose_tokens(self):
        """possibility to enrich some cryptic values with their human readable description"""
        tokens = list(self._tokens)
        return tokens

    @classmethod        
    def commands(cls):
        return ['DEF_ERPCommandSetDatabaseTime_____', ]
    
    def token_descriptions(self):
        return ['date', 'time']
    
    
class MarkForGetSolCtpProd(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def verbose_tokens(self):
        """possibility to enrich some cryptic values with their human readable description"""
        tokens = list(self._tokens)
        return tokens

    @classmethod        
    def commands(cls):
        return ['DEF_ERPCommandMarkForGetSolCtpProd', ]
    
    def token_descriptions(self):
        return ['process_area', 'process']    
        
        
class GetSolutionCtpProd(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def verbose_tokens(self):
        """possibility to enrich some cryptic values with their human readable description"""
        tokens = list(self._tokens)
        return tokens

    @classmethod        
    def commands(cls):
        return ['DEF_ERPCommandgetSolutionCtpProd__', ]
    
    def token_descriptions(self):
        return ['process_area', 'process']    
    
class GetSolutionCtp(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def verbose_tokens(self):
        """possibility to enrich some cryptic values with their human readable description"""
        tokens = list(self._tokens)
        return tokens

    @classmethod        
    def commands(cls):
        return ['DEF_ERPCommandgetSolutionCTP______', ]
    
    def token_descriptions(self):
        return ['process_area', 'process']     
    
    
class SetConfigParam(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def verbose_tokens(self):
        """possibility to enrich some cryptic values with their human readable description"""
        tokens = list(self._tokens)
        return tokens

    @classmethod        
    def commands(cls):
        return ['DEF_ERPCommandSetConfigParam______', ]
    
    def token_descriptions(self):
        return ['key', 'value'] 
    
    
class UpdateActivity(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def verbose_tokens(self):
        """possibility to enrich some cryptic values with their human readable description"""
        tokens = list(self._tokens)
        return tokens

    @classmethod        
    def commands(cls):
        return ['DEF_ERPCommandupdate_Activity_____', ]
    
    def token_descriptions(self):
        return ['process_area_head', 'process', 'part_process', 'act_pos', 'Akt_Art',
                'ident_act', 'start_date', 'end_date', 'fixed', 'start_time', 'end_time', 
                'Fertigungstyp', 'Fertig_gemeldet', 'Ruestklasse',] 
        
        
    
class UpdateResource(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def verbose_tokens(self):
        """possibility to enrich some cryptic values with their human readable description"""
        tokens = list(self._tokens)
        return tokens

    @classmethod        
    def commands(cls):
        return ['DEF_ERPCommandupdate_Resource_____', ]
    
    def token_descriptions(self):
        return ['', '', '', '', '',
                '', '', '', '', '', '', 
                '', '', '',]                           