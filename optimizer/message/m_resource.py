# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: m_resource.py
#
# description
"""\n\n
    M_Resource class
"""

from message.baseitem import BaseItem
from to_string import ToString

class M_Resource(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def __str__(self):
        text = "Ressource %s %s %s" % (self.resource(), self.resource_group(),
                                       ToString.resource_type(self.res_art()))
        return text

    def res_art(self):
        return int(self._tokens[0])

    def resource(self):
        return self._tokens[1]

    def resource_group(self):
        return self._tokens[2]

    def calendar(self):
        return self._tokens[3]

    def belastungsgrenze(self):
        return self.to_float(self._tokens[4])

    def intensity(self):
        return self.to_float(self._tokens[5])

    def is_engpass(self):
        return self._tokens[7] == '1'

    def is_ueberlast_ok(self):
        return self._tokens[8] == '1'

    def place(self):
        return self._tokens[9]

    def waiting_time(self):
        return self.to_float(self._tokens[10])

    def timeunit(self):
        return int(self._tokens[11])

    def weightfactor(self):
        return self.to_float(self._tokens[12])

    def is_setup_relevant(self):
        return self._tokens[13] == '1'

    def overload_intensity(self):
        return self.to_float(self._tokens[14])

    def ignore_intensity(self):
        return self._tokens[15] == '1'

    def res_key(self):
        return self.make_key(self.res_art(), self.resource())

    def verbose_tokens(self):
        """possibility to enrich some cryptic values with their human readable description"""
        tokens = list(self._tokens)
        self.verbose_token(0, ToString.resource_type, tokens)
        self.verbose_token(6, ToString.resource_meta_type, tokens)
        self.verbose_token(11, ToString.time_unit, tokens)
        self.verbose_token(17, ToString.time_unit, tokens)
        return tokens

    def headline_ids(self):
        return "%s %s" % (self.res_art(), self.resource())

    @classmethod
    def commands(cls):
        return ['DEF_ERPCommandcreate_M_Ressource__', ]

    def token_descriptions(self):
        if self.mode51():
            return  ['res_kind', 'res', 'res_group', 'cal', 'BelGr', 'intensity', '',
                     'is_bottleneck', 'intensity_ovl', 'place', 'waiting_time', 'waiting_timeunit',
                     'capacity_weight_factor']
                # , 'SetupRvt', 'IntOvl', 'IntIgn'] not in 5.1 available
        return ['res_kind', 'res', 'res_group', 'cal', 'BelGr', 'intensity', 'res_type',
                'is_bottleneck', 'is_possible_ovl', 'place', 'waiting_time', 'waiting_timeunit',
                'capacity_weight_factor', 'is_setup_relevant (unused)', 'intensity_ovl',
                'unlimited_intensity', 'buffer_time', 'buffer_time_unit', 'buffer_bound',
                'setup_matrix_id', 'sequence_range']


class M_ResAlt(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def res_art(self):
        return self._tokens[0]

    def alt_group(self):
        return self._tokens[1]

    def resource(self):
        return self._tokens[2]

    def priority(self):
        return self._tokens[3]

    def get_res_key(self):
        return self.make_key(self.res_art(), self.resource())

    def get_res_alt_key(self):
        return self.make_key(self.res_art(), self.alt_group(), self.resource())

    def get_alt_group_key(self):
        return self.make_key(self.res_art(), self.alt_group())

    @classmethod
    def commands(cls):
        return ['DEF_ERPCommandcreate_M_RessAlt____', ]

    def token_descriptions(self):
        return ['res_kind', 'alt_group', 'res', 'Prio']


class M_ResAltGroup(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def res_art(self):
        return self._tokens[0]

    def alt_group(self):
        return self._tokens[1]

    def get_alt_group_key(self):
        return self.make_key(self.res_art(), self.alt_group())

    @classmethod
    def commands(cls):
        return ['DEF_ERPCommandcreate_M_RessAltGr__', ]

    def token_descriptions(self):
        return ['res_kind', 'alt_group']



class UpdateResource(BaseItem):
    """update resource command"""
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    @classmethod
    def commands(cls):
        return ['DEF_ERPCommandupdateRessource_____']

    def token_descriptions(self):
        return ['res_kind', 'res']