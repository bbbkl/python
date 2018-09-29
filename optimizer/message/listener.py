# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: listener.py
#
# description
"""\n\n
    Miscellaneous commands from optimizer for listner/erp 
"""

from message.baseitem import BaseItem
from to_string import ToString

class APSCommandackSolutionCtpProd(BaseItem):
    """One material reason"""
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def proc_id(self):
        """get proc id"""
        return self._tokens[1]

    @classmethod
    def commands(cls):
        return ['DEF_APSCommandackSolutionCtpProd__', ]

    def token_descriptions(self):
        return ['process_area_head', 'process', 'Solution_found', '?', '?', '?', '?' ]


class JobContextCtp(BaseItem):
    """job context info optimizer -> ERP"""    
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)
        
    def headline_ids(self):
        """get headline for explained mode"""
        return "%s" % self._command.text()
        
    @classmethod
    def commands(cls):
        return ['DEF_ERPCommandsetJobContextCTP____', ]


    def token_descriptions(self):
        return ['JobKey', 'CompanyKey', 'ServerKey', 'ClientKey', 'ProcessKey', 'ArtikelKey', 'ArtVarKey', 'BgrFolge', 
                'DoAssignmentCheckAfterCTP', 'SetMaxProdMenge', 'create_XML' ]


class JobContextCtpProd(BaseItem):
    """job context info optimizer -> ERP"""    
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)
        
    def headline_ids(self):
        """get headline for explained mode"""
        return "%s" % self._command.text()
        
    @classmethod
    def commands(cls):
        return ['DEF_APSCommandCreate_JobContextSim', 
                'DEF_APSCommandset_JobContextCTPPrd',                 
                'DEF_ERPCommandsetJobContextCTPProd', ]


    def token_descriptions(self):
        return ['JobKey', 'CompanyKey', 'ServerKey', 'ClientKey', 'DoAssignmentCheckAfterCTP', 'create_XML' ] 
    
    
class JobContext(BaseItem):
    """job context info ERP -> optimizer"""    
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)
        
    def headline_ids(self):
        """get headline for explained mode"""
        return "%s" % self._command.text()
        
    @classmethod
    def commands(cls):
        return ['DEF_ERPCommandsetJobContext_______', 'DEF_APSCommandset_JobContext______', ]

    def token_descriptions(self):
        return ['JobKey', 'CompanyKey', 'ServerKey', 'DoRunDispo', 'SimScenarioObj' ]      
    
class NoSolutionPPA(BaseItem):
    """no sultion for process xyz optimizer -> ERP"""    
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)
        
    def headline_ids(self):
        """get headline for explained mode"""
        return "%s" % self._command.text()
        
    @classmethod
    def commands(cls):
        return ['DEF_APSCommandcreate_NoSoluitonPPA']

    def token_descriptions(self):
        return ['Process'] 
    
    
class ContTimePoint(BaseItem):
    """continous timepoint optimizer -> ERP"""    
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)
        
    def process_id(self):
        """get process id"""
        return self._tokens[2]

    def partproc_id(self):
        """get partproc id"""
        return self._tokens[3]

    def ident_akt(self):
        """get activity id"""
        return self._tokens[0]

        
    def headline_ids(self):
        """get headline for explained mode"""
        #return "%s" % self._command.text()
        return "%s %s %s" % (self.process_id(), self.partproc_id(), self.ident_akt())
        
    @classmethod
    def commands(cls):
        return ['DEF_APSCommandcreate_ContTimePoint']

    def token_descriptions(self):
        return ['IdentAct', 'ProcessArea', 'Process', 'PartProcess', 'SplitNo', 'Date', 'Time',
                'hasProduction', 'hasConsumption', 'OptimalDemand_Date', 'OptimalDemand_Time']    
    
    