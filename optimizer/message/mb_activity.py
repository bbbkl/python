# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: mb_activity.py
#
# description
"""\n\n
    MbActivity / ActDispatch class
"""

from message.baseitem import BaseItem
from to_string import ToString

class MbActivity(BaseItem):
    """One MbActivity"""
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def process_id(self):
        """get process id"""
        return self._tokens[9]

    def partproc_id(self):
        """get partproc id"""
        return self._tokens[5]

    def ident_akt(self):
        """get activity id"""
        return self._tokens[0]

    def is_on_critical_path(self):
        """true if activity is member of the crititcal path"""
        return self._tokens[7]=='1'

    def verbose_tokens(self):
        """possibility to enrich some cryptic values with their human readable description"""
        tokens = list(self._tokens)
        pos = self.token_descriptions().index('optimization_type')
        self.verbose_token(pos, ToString.optimization_type, tokens)
        return tokens       

    def headline_ids(self):
        """get headline for explained mode"""
        return "%s %s %s %d" % (self.process_id(), self.partproc_id(), self.ident_akt(), self.is_on_critical_path())

    @classmethod
    def commands(cls):
        return ['DEF_APSCommandcreate_MB_Aktivitaet', ]

    def token_descriptions(self):        
        return ['ident_act', 'start_date', 'start_time', 'end_date', 'end_time',
                'part_process', 'min_dlz',
                'is_on_critical_path', 'process_area', 'process', 'can_be_fixed',
                'start_date_optimal', 'start_time_optimal', 'end_date_optimal', 'end_time_optimal',
                'implicitly_fixed', 'optimization_type', 'setup_time_pct']


class ActDispatch(BaseItem):
    """One ActDispatch item"""
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def ident_akt(self):
        """get activity id"""
        return self._tokens[1]

    def starttime(self):
        """start date / time"""
        return "%s %s" % (self._tokens[2], self._tokens[3])

    def endtime(self):
        """end date / time"""
        return "%s %s" % (self._tokens[4], self._tokens[5])

    def headline_ids(self):
        """get headline for explained mode"""
        return "%s %s %s" % (self.ident_akt(), self.starttime(), self.endtime())

    @classmethod        
    def commands(cls):
        return ['DEF_APSCommandcreate_ActDispatch__', ]

    def token_descriptions(self):        
        return ['process_area', 'ident_act', 'start_date', 'start_time', 'end_date', 'end_time']
    
    
class ActSplit(BaseItem):
    """One ActDispatch item"""
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def ident_akt(self):
        """get activity id"""
        return self._tokens[0]

    def split_point(self):
        """split point"""
        return self._tokens[11]
    
    def starttime(self):
        """start date / time"""
        return "%s %s" % (self._tokens[1], self._tokens[2])

    def headline_ids(self):
        """get headline for explained mode"""
        return "%s %s %s" % (self.ident_akt(), self.split_point(), self.starttime())

    @classmethod        
    def commands(cls):
        return ['DEF_APSCommandcreate_MB_SplittAkt_', ]

    def token_descriptions(self):        
        return ['ident_act', 'start_date', 'start_time', 'end_date', 'end_time', 'part_process',
                'min_dlz', 'is_on_critical_path', 'process_area', 'process', 'can_be_fixed',
                'split_point',
                'start_date_optimal', 'start_time_optimal', 'end_date_optimal', 'end_time_optimal']



class BufferInfo(BaseItem):
    """One buffer info"""
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    @classmethod        
    def commands(cls):
        return ['DEF_APSCommandcreate_BufferInfo___', ]

    def token_descriptions(self):        
        return ['process', 'buffertime_tompllete', 'buffertime_left', 'buffertime_as_string [h]']
