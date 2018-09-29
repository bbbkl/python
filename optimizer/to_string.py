# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: to_string.py
#
# description
from builtins import classmethod
"""\n\n
    Base class for activity, ...
"""

def to_int(val):
    """turn given string value into a number, -1 for an empty string"""
    if val != '':
        return int(val)
    return -1

class ToString(object):
    """to string methods"""
        
    @classmethod
    def scheduling_obj_type(cls, val):
        """Scheduling type 
           OTUndefined    = -1,
           OTDemand       = 0,
           OTActivity     = 1,
           OTTempActivity = 2,
           OTPartProc     = 3,
           OTTempPartProc = 4
        """
        val = to_int(val)
        if val == 0: return 'Demand'
        if val == 1: return 'Activity'
        if val == 2: return 'TempActivity'
        if val == 3: return 'OTPartProc'
        if val == 4: return 'OTTempPartProc'
        return 'undefined'
        
    @classmethod
    def time_unit(cls, val):
        """time unit to string
           ETimeUnit_Undefined    = -1,
           ETimeUnit_Second       = 0,  // Sekunden
           ETimeUnit_Minute       = 1,  // Minuten
           ETimeUnit_Hour         = 2,  // Stunden
           ETimeUnit_WorkingDay   = 3,  // Arbeitstage 24 Stunden
           ETimeUnit_CalendarDay  = 4,  // Kalendertage 24 Stunden
           ETimeUnit_CalendarWeek = 5   // Kalenderwochen 24 Stunden * 7 Tage"""
        val = to_int(val)
        if val == 0: return 'Sekunden'
        if val == 1: return 'Minuten'
        if val == 2: return 'Stunden'
        if val == 3: return 'Arbeitstage'
        if val == 4: return 'Kalendertage'
        if val == 5: return 'Kalenderwochen'
        return 'undefined'

    @classmethod
    def aob(cls, val):
        """aob to string
           ETrAOB_UNKNOWN = -1,
           ETrAOB_BB      = 0,
           ETrAOB_BA      = 1,
           ETrAOB_EB      = 2,
           ETrAOB_EA      = 3,
           ETrAOB_AAFIX   = 4,
           ETrAOB_EEFIX   = 5,
           ETrAOB_EAFIX   = 6,
           ETrAOB_AA      = 7,
           ETrAOB_EE      = 8,
           ETrAOB_BBFIX   = 9,
           ETrAOB_EARUEST = 10,
           ETrAOB_EEPARTLOT = 70"""
        val = to_int(val)
        if val == 0: return 'BB'
        if val == 1: return 'BA'
        if val == 2: return 'EB'
        if val == 3: return 'EA'
        if val == 4: return 'AAFIX'
        if val == 5: return 'EEFIX'
        if val == 6: return 'EAFIX'
        if val == 7: return 'AA'
        if val == 8: return 'EE'
        if val == 9: return 'BBFIX'
        if val == 10: return 'EARUEST'
        if val == 70: return 'EEPARTLOT'
        return 'undefined'
    
    @classmethod
    def time_condition(cls, val):
        """time condition to string
           ETimeCondition_none         = 0,
           ETimeCondition_StartsAt     = 1,
           ETimeCondition_EndsBefore   = 2,
           ETimeCondition_StartsAfter  = 3,
           ETimeCondition_StartsBefore = 4,
           ETimeCondition_EndsAfter    = 5,
           ETimeCondition_EndsAt       = 6"""
        val = to_int(val)
        if val == 0: return 'Ohne'
        if val == 1: return 'StartsAt'
        if val == 2: return 'EndsBefore'
        if val == 3: return 'StartsAfter'
        if val == 4: return 'StartsBefore'
        if val == 5: return 'EndsAfter'
        if val == 6: return 'EndsAt'
        return 'undefined'
    
    @classmethod
    def activity_type(cls, val):
        """activity type to string
           EActivityType_Production = 0,
           EActivityType_Foreign    = 1,
           EActivityType_Verfahren  = 2,
           EActivityType_Transport  = 3,
           EActivityType_Flaeche    = 4,
           EActivityType_StartEnd   = 5,  // Durchlaufzeit Aktivität
           EActivityType_FlexLength = 15"""
        val = to_int(val)
        if val == 0: return 'Produktion'
        if val == 1: return 'Fremdarbeit'
        if val == 2: return 'Verfahren'
        if val == 3: return 'Transport'
        if val == 4: return 'Flaeche' 
        if val == 5: return 'Durchlaufzeit'
        if val == 15: return 'FlexLength'
        return 'undefined'
    
    @classmethod
    def resource_meta_type(cls, val):
        """resourc meta type to string
        pa_PM_ResourceTypeSingle    1
        pa_PM_ResourceTypeGroup     2
        pa_PM_ResourceTypeCosts     3
        """
        val = to_int(val)
        if val == 1: return "Unnaere"
        if val == 2: return "Gruppe"
        if val == 3: return "Kosten"
        return 'undefined'
    
    @classmethod
    def resource_type(cls, val):
        """resource type to string
           EResourceTypeERP_CompanyCalERP = -100,
           EResourceTypeERP_unknownERP    = 0,
           EResourceTypeERP_MachineERP    = 1,
           EResourceTypeERP_ManERP        = 2,
           EResourceTypeERP_ToolERP       = 3,
           EResourceTypeERP_TransportERP  = 4,
           EResourceTypeERP_ProcedureERP  = 5,
           EResourceTypeERP_FloorERP      = 6,
           EResourceTypeERP_WorkPlaceERP  = 7,
           EResourceTypeERP_MaterialERP   = 8"""
        val = to_int(val)
        if val == -100: return 'Betriebskalender'
        if val == 1: return 'Maschine'
        if val == 2: return 'Mensch'
        if val == 3: return 'Werkzeug'
        if val == 4: return 'Transport'
        if val == 5: return 'Verfahren'
        if val == 6: return 'Flaeche'
        if val == 7: return 'Arbeitsplatz'
        if val == 8: return 'Material'
        return 'undefined'
    
    @classmethod
    def last_opt_type(cls, val):
        """
         EOptimizationType_Unknown            = -1,
         EOptimizationType_Standard           = 0,
         EOptimizationType_OverLoadAll        = 1,
         EOptimizationType_OverLoadMat        = 2,
         EOptimizationType_OverLoadRes        = 3,
         EOptimizationType_OverLoadWithNoLoad = 4
        """
        val = to_int(val)
        if val == 0: return 'Standard'
        if val == 1: return 'OverLoadAll'
        if val == 2: return 'OverLoadMat'
        if val == 3: return 'OverLoadRes'
        if val == 4: return 'Durchlauf'
        return 'undefined'
    
    @classmethod
    def last_opt_target(cls, val):
        """
        EOptimizationTarget_Unknown         = -1,
        EOptimizationTarget_DueDate         = 0,
        EOptimizationTarget_EarlyAsPossible = 1
        """
        val = to_int(val)
        if val == 0: return 'due_date'
        if val == 1: return 'Fruehestmoeglich'
        return 'undefined'
    
    @classmethod
    def optimization_type(cls, val):
        """
        EOptimizationType_Unknown            = -1,
        EOptimizationType_Standard           = 0,
        EOptimizationType_OverLoadAll        = 1,
        EOptimizationType_OverLoadMat        = 2,
        EOptimizationType_OverLoadRes        = 3,
        EOptimizationType_OverLoadWithNoLoad = 4,
        EOptimizationType_OverLoadSpecific   = 5
        """
        val = to_int(val)
        if val == 0: return 'std'
        if val == 1: return 'ovl_all'
        if val == 2: return 'ovl_mat'
        if val == 3: return 'ovl_res'
        if val == 4: return 'ovl_noload'
        if val == 5: return 'ovl_specific'
        return 'undefined'
    
    @classmethod
    def determination_type(cls, val):
        """
        ETRD_Before:  return 0; // 0 - ERP REASON BEFORE blockwise
        ETRD_During:  return 1; // 1 - ERP REASON DURING blockwise
        ETRD_After:   return 2; // 2 - ERP REASON AFTER  blockwise (deprecated)
        ETRD_Overall: return 2; // 2 - ERP REASON AFTER  overall
        """
        val = to_int(val)
        if val == 0: return 'before'
        if val == 1: return 'during'
        if val == 2: return 'after'
        if val == 3: return 'overall'
        return 'undefined'
    
    @classmethod
    def timebound_originator(cls, val):
        """
        ETBODatabaseTime: // fall through
        ETBOStandard:         return 0;
        ETBOReservation:      return 1;
        ETBOFixedPredecessor: return 2;
        ETBOProcess:          return 3;
        """
        val = to_int(val)
        if val == 0: return 'standard'
        if val == 1: return 'reservation'
        if val == 2: return 'fixed_predecessor'
        if val == 3: return 'process'
        return 'undefined'
    
    @classmethod
    def fertigungstyp(cls, val):
        """
        #define DEF_APS_Temp_Aktivity     0
        #define DEF_APS_MB_Aktivity       1
        #define DEF_APS_Dummy_Aktivity    2
        """
        val = to_int(val)
        if val == 0: return "Temp"
        if val == 1: return "MB"
        if val == 2: return "Dummy"
        return 'undefined'
    
    @classmethod
    def kommlager(cls, val):
        """
        ECro_Without,
        ECro_Possible,
        ECro_Mandatory
        """
        val = to_int(val)
        if val == 0: return "ECro_Without"
        if val == 1: return "ECro_Possible"
        if val == 2: return "ECro_Mandatory"
        return 'undefined'
    
    @classmethod
    def structure_reason_subtype(cls, val):
        val = to_int(val)
        if val == 0: return "default"
        if val == 1: return "all_fixed_or_done"
        if val == 2: return "all_fixed"
        if val == 3: return "all_done"
        
    @classmethod
    def setup_property_type(cls, val):
        val = to_int(val)                           #ESetupMatrixPropertyType
        if val == 1: return "assembly_part"         # Produces
        if val == 2: return "assembly_part_feature" # ProducesFeature
        if val == 3: return "bomline_part"          # Consumes
        if val == 4: return "resource"              # Resource
        if val == 5: return "operation_class"       # ActivityClass
        if val == 6: return "bomline_part_feature"  # ConsumesFeature
        if val == 7: return "resource_feature"      # ResourceFeature
        return 'undefined'
    
    @classmethod
    def sorting_function(cls, val):
        val = to_int(val)
        if val == 1: return "Equal"
        if val == 2: return "Ascending" 
        if val == 3: return "Descending"
        return 'undefined'