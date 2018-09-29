# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: calendar.py
#
# description
"""\n\n
    Calendar class
"""

from message.baseitem import BaseItem

class S_BetriebKal(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)
        
    def calendar_id(self):
        """get id"""
        return "%s_calendar_%s" % (self._tokens[1], self._tokens[1]) 

    @classmethod        
    def commands(cls):
        return ['DEF_ERPCommandcreate_BetriebsKal__']

    def token_descriptions(self):
        return ['free_day', 'cal'] 

class M_Kalender(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)
        
    @classmethod        
    def commands(cls):
        return ['DEF_ERPCommandcreate_M_Kalender___']
    
    def token_descriptions(self):
        return ['cal_type', 'cal']
    
class M_KalenderZeit(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)
        
    @classmethod        
    def commands(cls):
        return ['DEF_ERPCommandcreate_M_KalZeit____']
    
    def token_descriptions(self):
        return ['cal_type', 'cal', 'date', 
                'start', 'end', 'intensity', 'intensity_ovl']    

class M_IntKalender(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)
        
    @classmethod        
    def commands(cls):
        return ['DEF_ERPCommandcreate_M_IntKal_____']
    
    def token_descriptions(self):
        return ['cal_type', 'cal', 'date', 
                'start', 'end', 'intensity', 'res_kind',
                'res', 'intensity_ovl']    
        
class M_KalDatum(BaseItem):
    """one calendar block"""
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)    
        
    @classmethod        
    def commands(cls):
        return ['DEF_ERPCommandcreate_M_KalDatum___']
    
    def token_descriptions(self):
        return ['cal_type', 'cal', 'start_date', 
                'start_time', 'end_date', 'end_time', 'intensity'] 
        
        
class UpdateCalendar(BaseItem):
    """update calendar command"""
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)    
        
    @classmethod        
    def commands(cls):
        return ['DEF_ERPCommandupdateCalendar______']
    
    def token_descriptions(self):
        return ['cal_type', 'cal']  