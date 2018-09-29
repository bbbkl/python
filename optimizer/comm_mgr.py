# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: comm_mgr.py
#
# description
"""\n\n
    CommMgr class
"""
from message.tr_activity import TrActivity
from message.tr_resource import TrResource
from message.m_resource import M_Resource, M_ResAlt, M_ResAltGroup
from message.tr_process import TrProcess
from message.serverinfo import P_ZeitMngEinh
from message.s_article import SArticle
from message.md_artikel import MD_Artikel
from message.ml_artort import ML_ArtOrt
from message.m_dispobew import M_DispoBew

class CommMgr(object):
    def __init__(self, message_items):
        self._items = message_items
        
    def add_resources_to_activities(self):
        """CreateResHelpTable"""
        resources = [item for item in self._items if isinstance(item, TrResource)]
        resource_dict = {}
        for item in resources:
            key = item.activity_key()
            resource_dict.setdefault(key, [])
            resource_dict[key].append(item)
            
        activities = [item for item in self._items if isinstance(item, TrActivity)]
        for item in activities:
            key = item.ident_part_proc_key()
            if key in resource_dict:
                item.set_resources(resource_dict[key])
                
    def add_processes_to_activities(self):
        processes = [item for item in self._items if isinstance(item, TrProcess)]
        process_dict = {}
        for item in processes:
            process_dict[item.ident_proc_key()] = item
            
        activities = [item for item in self._items if isinstance(item, TrActivity)]
        for item in activities:
            key = item.process_key_rueck_nr()
            if key in process_dict:
                item.set_process(process_dict[key])
                
    def add_zeitmengeneinheit_to_activities(self):
        units = [item for item in self._items if isinstance(item, P_ZeitMngEinh)]
        unit_dict = {}
        for unit in units:
            unit_dict[unit.zeitmengeneinheit()] = unit.factor()
            
        activities = [item for item in self._items if isinstance(item, TrActivity)]
        for item in activities:
            item.set_zeitmengeneinheit(unit_dict)
                
    def combine_resources(self):
        m_resources = [item for item in self._items if isinstance(item, M_Resource)]
        m_resource_dict = {}
        for item in m_resources:
            key = item.res_key()
            m_resource_dict.setdefault(key, [])
            m_resource_dict[key].append(item)
            
        resource_alt_groups = [item for item in self._items if isinstance(item, M_ResAltGroup)]
        group_dict = {}
        for group in resource_alt_groups:
            group_dict[group.get_alt_group_key()] = []
        
        res_alts = [item for item in self._items if isinstance(item, M_ResAlt)]
        for res_alt in res_alts:
            group = res_alt.get_alt_group_key()
            res_key = res_alt.get_res_key()
            group_dict[group].extend(m_resource_dict[res_key])
            
        resources = [item for item in self._items if isinstance(item, TrResource)]
        for resource in resources:
            res_key = resource.res_key()
            if res_key in m_resource_dict:
                resource.set_m_resources(m_resource_dict[res_key])
            group_key = resource.get_alt_group_key()
            if group_key in group_dict:
                resource.set_alt_res_group(group_dict[group_key])
                
    def combine_artikel(self):
        artikels = [item for item in self._items if isinstance(item, SArticle)]
        artikel_dict = {}
        for item in artikels:
            artikel_dict[item.article_id()] = item
        
        # add dispo parameter to artikel
        dispo_params = [item for item in self._items if isinstance(item, MD_Artikel)]
        for item in dispo_params:
            artikel = artikel_dict[item.article_id()]
            artikel.add_dispo_parameter(item)
            
        # add artort to artikel
        artort_items = [item for item in self._items if isinstance(item, ML_ArtOrt)]
        for item in artort_items:
            artikel = artikel_dict[item.article_id()]
            artikel.add_ort(item)
            
        # add dispo bewegungen
        dispobew_items = [item for item in self._items if isinstance(item, M_DispoBew)]
        for item in dispobew_items:
            artikel = artikel_dict[item.article_id()]
            artikel.add_dispobew(item)