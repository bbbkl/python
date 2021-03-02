# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: marterial.py
#
# description
"""\n\n
    TrMaterial class
"""

from message.baseitem import BaseItem

class TrMaterial(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def process_id(self):
        """get id"""
        return self._tokens[1]

    def partprocess_id(self):
        """get part process id (rueckmeldenummer)"""
        return self._tokens[2]

    def article(self):
        """return part id"""
        return self._tokens[5]

    @classmethod
    def commands(cls):
        return ['DEF_ERPCommandcreate_Material_____', ]

    def headline_ids(self):
        return "%s %s %s" % (self.process_id(), self.partprocess_id(), self.article())

    def token_descriptions(self):
        if self.mode51():
            return ['process_area', 'process', 'part_process', 'act_pos',
                'res_position', 'part', 'part_variant', 'demand_quantity',
                'ident_act', 'mrp_area',
                'LagerOrt', # not in 5.3
                'Zeilenart', 'Belegart_Herkunft',
                'Schluessel_Herkunft', 'lot']
            #, 'demand_quantity_total', 'continious'] not in 5.3
        return ['process_area', 'process', 'part_process', 'act_pos',
                'res_position', 'part', 'part_variant', 'demand_quantity',
                'ident_act', 'mrp_area', 'Zeilenart', 'Belegart_Herkunft',
                'Schluessel_Herkunft', 'lot', 'demand_quantity_total', 'continious', 'cro',
                'reservation']


class TrOverloadMaterial(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def part(self):
        return self._tokens[0]
    
    def variant(self):
        return self._tokens[1]

    @classmethod
    def commands(cls):
        return ['DEF_ERPCommandcreate_Overload_Mat_', ]

    def token_descriptions(self):
        return ['part', 'part_variant']

class TrOverloadResource(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def res_art(self):
        return self._tokens[0]
    
    def res(self):
        return self._tokens[1]

    @classmethod
    def commands(cls):
        return ['DEF_ERPCommandcreate_Overload_Res_', ]

    def token_descriptions(self):
        return ['res_kind', 'res']
    
    
class TrUpdateResource(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)
    
    def res_art(self):
        return self._tokens[0]
    
    def res(self):
        return self._tokens[1]

    @classmethod
    def commands(cls):
        return ['DEF_ERPCommandupdateRessource_____', ]

    def token_descriptions(self):
        return ['res_kind', 'res']
