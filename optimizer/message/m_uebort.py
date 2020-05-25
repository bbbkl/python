# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: m_uebort.py
#
# description
"""\n\n
    M_UebOrt class
"""

from message.baseitem import BaseItem
from to_string import ToString

class M_UebOrt(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def adressnr(self):
        """get adress number"""
        return self._tokens[0]

    def von_ort(self):
        """get von ort"""
        return self._tokens[1]

    def nach_ort(self):
        """get nach ort"""
        return self._tokens[2]

    def transition_time(self):
        """get transition time"""
        return int(self._tokens[3])

    def transition_time_unit(self):
        """get transition time unit"""
        return int(self._tokens[4])

    def dynamic_buffer_time(self):
        """get dynamic buffer time"""
        pos = 5
        if len(self._tokens) > pos:
            return int(self._tokens[pos])
        return 0

    def dynamic_buffer_time_unit(self):
        """get dynamic buffer time unit"""
        pos = 6
        if len(self._tokens) > pos:
            return int(self._tokens[pos])
        return 0

    def verbose_tokens(self):
        """possibility to enrich some cryptic values with their human readable description"""
        tokens = list(self._tokens)
        self.verbose_token(4, ToString.time_unit, tokens)
        self.verbose_token(6, ToString.time_unit, tokens)
        return tokens

    @classmethod
    def commands(cls):
        return ['DEF_ERPCommandcreate_M_UebOrt_____', ]

    def token_descriptions(self):
        return ['Adress_Nr', 'Von_Ort',  'Nach_Ort', 'transport_time', 'transport_time_unit',
                'buffer_time', 'buffer_time_unit', 'buffer_bound']
