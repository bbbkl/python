# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: m_uebadresse.py
#
# description
"""\n\n
    M_UebAdresse class
"""

from message.baseitem import BaseItem
from to_string import ToString

class M_UebAdresse(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def von_adresse(self):
        """get von adresse"""
        return self._tokens[0]

    def nach_adresse(self):
        """get nach adresse"""
        return self._tokens[1]

    def transition_time(self):
        """get transition time"""
        return int(self._tokens[2])

    def transition_time_unit(self):
        """get transition time unit"""
        return int(self._tokens[3])

    def dynamic_buffer_time(self):
        """get dynamic buffer time"""
        pos = 4
        if len(self._tokens) > pos:
            return int(self._tokens[pos])
        return 0

    def dynamic_buffer_time_unit(self):
        """get dynamic buffer time unit"""
        pos = 5
        if len(self._tokens) > pos:
            return int(self._tokens[pos])
        return 0

    def headline_ids(self):
        """get headline for explained mode"""
        return "%s %s" % (self.von_adresse(), self.nach_adresse())

    def verbose_tokens(self):
        """possibility to enrich some cryptic values with their human readable description"""
        tokens = list(self._tokens)
        self.verbose_token(3, ToString.time_unit, tokens)
        self.verbose_token(5, ToString.time_unit, tokens)
        return tokens

    @classmethod
    def commands(cls):
        return ['DEF_ERPCommandcreate_M_UebAdresse_', ]

    def token_descriptions(self):
        return ['Von_Adresse', 'Nach_Adresse',  'transport_time', 'transport_time_unit',
                'buffer_time', 'buffer_time_unit', 'buffer_bound']
