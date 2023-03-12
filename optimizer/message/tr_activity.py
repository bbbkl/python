# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: activity.py
#
# description
"""\n\n
    TrActivity class
"""

from datetime import datetime, timedelta
from message.baseitem import BaseItem
from to_string import ToString

class TrActivity(BaseItem):
    """One TrActivity"""
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)
        self._resources = []
        self._process = None
        self._zeitmengeneinheit_dict = {}
        
    # class variable
    _server_date = None
    
    @classmethod
    def set_server_date(cls, val):
        """set server time"""
        TrActivity._server_date = val
        
    @classmethod
    def check_for_reservation(cls, dateval):
        if dateval != '' and  TrActivity._server_date is not None and dateval != TrActivity._server_date:
            return 'reservation/stable_area'
        return ''
        
    def __str__(self):
        return "activity pid: % 15s, id: %s, fix: %s, start: %s, end: %s" % \
            (self.process_id(), self.ident_akt(), self.fixiert() and "1" or "0",
             self.start_time(), self.end_time())
        
    def process_id(self):
        """get actitiy's process id"""
        return self._tokens[1]
    
    def process_bereich(self):
        """get process bereich"""
        return self._tokens[0]
    
    def process_bereich_orig(self):
        pos = 38
        if len(self._tokens) > pos:
            return self._tokens[pos] 
        return self.process_bereich()
    
    def partproc_id(self):
        """get part process"""
        return self._tokens[2]
    
    def akt_pos(self):
        """get activity position"""
        return int(self._tokens[3])
    
    def act_art(self):
        return ToString.activity_type(self._tokens[4])
    
    def ident_akt(self):
        """getIdentAkt"""
        return self._tokens[5]
    
    def start_time(self):
        """get start time: day & time"""
        day = datetime.strptime(self._tokens[14], "%d.%m.%Y")
        seconds = timedelta(0, int(self._tokens[20]))
        return day + seconds
    
    def end_time(self):
        """get end time: day & time"""
        day = datetime.strptime(self._tokens[15], "%d.%m.%Y")
        seconds = timedelta(0, int(self._tokens[21]))
        return day + seconds
    
    def tr(self):
        """ruestzeit"""
        return self.to_float(self._tokens[9])
    
    def te(self):
        return self.to_float(self._tokens[10])
    
    def zeitmengeneinheit(self):
        return int(self._tokens[13])
    
    def fixiert(self):
        """return status fixiert"""
        return 0 != int(self._tokens[16])
    
    def time_condition(self):
        """BedArt"""
        return int(self._tokens(18))
    
    def zeitraum_einheit(self):
        return 1 # int(self._tokens[25])
    
    def done(self):
        """ fertig gemeldet """
        return 1 == int(self._tokens[29])
    
    def ident_part_proc_key(self):
        return self.make_key(self.process_bereich_orig(), self.process_id(), self.partproc_id(), self.ident_akt())
    
    def process_key_rueck_nr(self):
        return self.make_key(self.process_bereich_orig(), self.process_id(), self.partproc_id())
        
    def get_base_resource(self):
        for resource in self._resources:
            if resource.is_basis_resource():
                return resource
        if len(self._resources) > 0:
            return self._resources[-1]
        return None
    
    def get_total_time(self):
        time_tr = self.tr()
        time_te = self.te() / self.get_intensity()
        secs_tr = self.get_time_in_seconds(time_tr, self.zeitraum_einheit())
        secs_te = self.get_time_in_seconds(time_te, self.zeitraum_einheit())
        secs_te /= self.get_timelot_unit()
        quantity = self.get_process().quantity()
        time_proc = secs_tr + secs_te * quantity
        time_proc /= 60 # seocnds to minutes
        #time_proc = int(time_proc) # ceil
        return time_proc
    
    def get_intensity(self):
        intensity = 1.0 # default
        base_resource = self.get_base_resource()
        if base_resource is not None:
            intensity = base_resource.intensity()
            if intensity <= 0.05:
                res_art = ToString.resource_type(base_resource.res_art())
                print("INVALID intensity of %05.2f, process: %s, activity: %s, resource: %s (%s)" % 
                          (intensity, self.process_id(), self.ident_akt(), base_resource.resource(), res_art))
        return intensity
    
    def get_belastungsgrenze(self):
        """ApsCommunicationsMgr::GetUtilizationFactor"""
        bgr = 100 # default
        base_resource = self.get_base_resource()
        if base_resource is not None:
            m_resource = base_resource.get_resource()
            if m_resource is not None:
                bgr = m_resource.belastungsgrenze()
                if bgr <= 5:
                    res_art = ToString.resource_type(m_resource.res_art())
                    print("INVALID belastungsgrenze of %d, process: %s, activity: %s, resource: %s (%s)" % 
                          (bgr, self.process_id(), self.ident_akt(), m_resource.resource(), res_art))
                    if bgr == 0:
                        bgr = 100
        return bgr
    
    def get_total_time_with_belastungsgrenze(self):
        minutes = self.get_total_time()
        bgr = self.get_belastungsgrenze()
        minutes *= 100
        minutes /= bgr
        minutes = int(minutes + 0.5) # round
        return minutes
    
    def get_server_time(self, seconds, server_time_interval='minutes'):
        if server_time_interval == 'minutes':
            return seconds / 60
        return seconds / (60 * 60) # hours
    
    def get_time_in_seconds(self, time_value, time_unit):
        if time_unit == 0: return time_value
        if time_unit == 1: return time_value * 60
        if time_unit == 2: return time_value * 60 * 60
        if time_unit == 3 or time_unit == 4: return time_value * 60 * 60 * 24
        if time_unit == 5: return time_value * 60 * 60 * 24 * 7
        return None
    
    def get_timelot_unit(self):
        result = 1.0 # default
        if self.act_art() == 'Production':
            if self.zeitmengeneinheit() in self._zeitmengeneinheit_dict:
                result = self._zeitmengeneinheit_dict[self.zeitmengeneinheit()]
        return result
    
    def set_resources(self, resources):
        self._resources = resources
    
    def set_zeitmengeneinheit(self, zeitmengeneinheit_dict):
        self._zeitmengeneinheit_dict = zeitmengeneinheit_dict
    
    def get_process(self):
        return self._process
    
    def set_process(self, process):
        self._process = process
        
    @classmethod
    def unfix(clscls, tokens):
        tokens[16] = '0' # fixed flag
        #tokens[29] = '0' # done flag
        return tokens
       
    def verbose_tokens(self):
        """possibility to enrich some cryptic values with their human readable description"""
        tokens = list(self._tokens)
        self.verbose_token(4, ToString.activity_type, tokens)
        self.verbose_token(8, ToString.time_unit, tokens)
        self.verbose_token(11, ToString.time_unit, tokens)
        self.verbose_token(12, ToString.time_unit, tokens)
        self.verbose_token(18, ToString.time_condition, tokens)
        self.verbose_token(19, TrActivity.check_for_reservation, tokens) # Fixtermin
        self.verbose_token(25, ToString.time_unit, tokens)
        self.verbose_token(27, ToString.time_unit, tokens)
        self.verbose_token(28, ToString.fertigungstyp, tokens) 
        return tokens       
       
    def headline_ids(self):
        return "%s %s %d %s %d" % (self.process_id(), self.partproc_id(), self.akt_pos(), self.ident_akt(), self.fixiert())   
        
    @classmethod        
    def commands(cls):
        return ['DEF_ERPCommandcreate_Activity_____', ]
    
    def token_descriptions(self):
        if self.mode51():
            return ['process_area_head', 'process', 'part_process', 'act_pos', 'Akt_Art',
                'ident_act', 'Zeitwahl', 'Zeit', 'Zeit_Einheit', 'TR', 'TE',
                'TR_timeunit', 'TE_timeunit', 'Zeitmengen_Einheit', 'start_date',
                'end_date', 'Fixiert', 'condition_date', 'condition_type', 'mat_reservation_date',
                'start_time', 'end_time', 
                '', '', # 5.1 'for compatibility usage'
                'Unterbrechbar', '#Unterbrechungen', 
                'Zeitraum', 'Zeitraum_Einheit', 'Min_Zwischenzeit', 'Min_Zwischenzeit_Einheit',
                'Fertigungstyp', 'Fertig_gemeldet', 'cal', 'activity_class',
                #, 'Partial_lot', // not in 5.1
                #'Total_lot_size', 'TRTotal', 'TETotal', 'Continous_production', // not in 5.1
                #'Continous_demand', // not in 5.1
                'PBO']
        
        return ['process_area_head', 'process', 'part_process', 'act_pos', 'Akt_Art',
                'ident_act', 'Zeitwahl', 'Zeit', 'Zeit_einheit', 'TR (deprecated with setup opt)', 'TE',
                'TR_timeunit', 'TE_timeunit', 'Zeitmengen_Einheit', 'start_date',
                'end_date', 'Fixiert', 'condition_date', 'condition_type', 'mat_reservation_date',
                'start_time', 'end_time', 'Unterbrechbar', '#Unterbrechungen', 
                'Zeitraum', 'Zeitraum_einheit', 'Min_Zwischenzeit', 'Min_Zwischenzeit_Einheit',
                'Fertigungstyp', 'Fertig_gemeldet', 'cal', 'activity_class', 'partial_lot',
                'total_lot_size', 'TR_total (deprecated with setup opt)', 'TE_total', 'continous_production',
                'continous_demand', 'process_area', 'Pufferaktivitaet',
                'setup_time_default', 'setup_time_actual', 'is_setup_activity', 
                'duedate_date', 'duedate_time']
