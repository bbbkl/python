# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: setup_matrix.py
#
# description
"""\n\n
    setup matrix related classes
"""

import datetime
from message.baseitem import BaseItem
from to_string import ToString

class SetupMatrix(BaseItem):
    """setup matrix"""
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)
        
    @classmethod        
    def commands(cls):
        return ['DEF_ERPCommandcreate_SetupMatrix__', ]
    
    def token_descriptions(self):
        return ['setup_matrix_id', 'horizon', 'interval', 'default_cost']
    
        
class SetupMatrixEntry(BaseItem):      
    """setup matrix entry"""
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)
        
    @classmethod        
    def commands(cls):
        return ['DEF_ERPCommandcreate_SetupMatrixEn', ]
    
    def token_descriptions(self):
        return ['setup_matrix_id', 'setup_time', 'penalty points',
                
                'from_property_type', 'from_classification_system', 'from_feature', 
                'from_specifictaion', 'from_part', 'from_part_variant', 'from_activity_class', 
                'from_resource_type', 'from_resesource',
                
                'to_property_type', 'to_classification_system', 'to_feature', 
                'to_specifictaion', 'to_part', 'to_part_variant', 'to_activity_class', 
                'to_resource_type', 'to_resource']
    
    def verbose_tokens(self):
        """possibility to enrich some cryptic values with their human readable description"""
        tokens = list(self._tokens)
        self.verbose_token(3, ToString.setup_property_type, tokens)
        self.verbose_token(12, ToString.setup_property_type, tokens)
        
        self.verbose_token(10, ToString.resource_type, tokens)
        self.verbose_token(19, ToString.resource_type, tokens)
        return tokens   
    
class SetupPartFeature(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)
        
    def zeitmengeneinheit(self):
        return int(self._tokens[0])
        
    @classmethod        
    def commands(cls):
        return ['DEF_ERPCommandcreate_SetupPartFeat', ]
    
    def token_descriptions(self):
        return ['part', 'classification_system', 'feature', 'specification']
    
class SetupResourceFeature(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)
        
    def zeitmengeneinheit(self):
        return int(self._tokens[0])
        
    @classmethod        
    def commands(cls):
        return ['DEF_ERPCommandcreate_SetupResFeat_', ]
    
    def token_descriptions(self):
        return ['resource', 'resource_type', 'classification_system', 'feature', 'specification']    



class SetupMatrixDefinition(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)
        
    @classmethod        
    def commands(cls):
        return ['DEF_ERPCommandcreate_SetupMatrixDf', ]
    
    def verbose_tokens(self):
        """possibility to enrich some cryptic values with their human readable description"""
        tokens = list(self._tokens)
        self.verbose_token(1, ToString.setup_property_type, tokens)
        self.verbose_token(4, ToString.sorting_function, tokens)
        return tokens
    
    def token_descriptions(self):
        return ['setup_matrix_id', 'setup_matrix_property_tpye', 'classification_system', 'feature',
                 'sorting_function', 'sorting_level', 'setup_time', 'position']      