# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: serverinfo.py
#
# description
"""\n\n
    Serverinfo class
"""

import datetime
from message.baseitem import BaseItem
from message.tr_activity import TrActivity

class ServerInfo(BaseItem):
    """Server info"""
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)
        TrActivity.set_server_date(self._tokens[0])
        
    @classmethod        
    def commands(cls):
        return ['DEF_ERPCommandsetServer___________', ]
    
    def token_descriptions(self):
        if self.mode51():
            return ['Serverdate', 'Servertime', 'Termin_Fak', 'Durch_Fak', 'Kap_Fak',
                'Berechnungszeit', 'Schrittweite', 'Horizont', 'Gesamthorizont', 'Frozen_zone', 
                'Termin_Verfr_Fak', 'Aktuelle_Opt_Num', 
                'MinVerbesserung'] # diff to 5.3
        return ['Serverdate', 'Servertime', 'TerminFak', 'DurchFak', 'KapFak',
                'Berechnungszeit', 'Schrittweite', '', 'Gesamthorizont', 'Frozen_zone', 
                'Termin_Verfr_Fak', 'Aktuelle_Opt_Num', 'Gründe_pro_BG_mit_WT', 'simulation']
    
    def time(self):
        """get server time"""
        # 17.02.2012    11:22
        date = datetime.datetime.strptime(self._tokens[0], "%d.%m.%Y")
        time = datetime.datetime.strptime(self._tokens[1], "%H:%M")
        return datetime.datetime.combine(date.date(), time.time())
    
    def server_time_interval(self):
        """either 'minutes' or 'hours'"""
        if self._tokens[6] == 'M': return 'minutes'
        return 'hours'
        
class CheckErpID(BaseItem):      
    """ERP version check"""
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)
        
    @classmethod        
    def commands(cls):
        return ['DEF_ERPCommandCheckErpID__________', ]
    
    def token_descriptions(self):
        return ['Version', 'Number']
        
class P_ZeitMngEinh(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)
        
    def zeitmengeneinheit(self):
        return int(self._tokens[0])
    
    def factor(self):
        return self.to_float(self._tokens[1])
        
    @classmethod        
    def commands(cls):
        return ['DEF_ERPCommandcreate_P_ZeitMngEinh', ]
    
    def token_descriptions(self):
        return ['Zeitmengeneinheit', 'Faktor']
    
class LicInfo(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)
        
    @classmethod        
    def commands(cls):
        return ['DEF_ERPCommandLicensedModules_____', ]
    
    def token_descriptions(self):
        return ['modules']
