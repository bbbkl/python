# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: process.py
#
# description
"""\n\n
    TrProcess class
"""

from message.baseitem import BaseItem
from to_string import ToString

class TrProcess(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def process_bereich(self):
        return self._tokens[0]

    def process_id(self):
        """get id"""
        return self._tokens[1]

    def partproc_id(self):
        return int(self._tokens[2])

    def article(self):
        return self._tokens[3]

    def quantity(self):
        """produktionsmenge"""
        return self.to_float(self._tokens[6])

    def is_head(self):
        return self._tokens[16] == '1'

    def process_bereich_orig(self):
        pos = 25
        if len(self._tokens) > pos:
            return self._tokens[pos]
        return self.process_bereich()

    def ident_proc_key(self):
        return self.make_key(self.process_bereich_orig(), self.process_id(), self.partproc_id())

    def verbose_tokens(self):
        """possibility to enrich some cryptic values with their human readable description"""
        tokens = list(self._tokens)
        self.verbose_token(18, ToString.last_opt_type, tokens)
        self.verbose_token(19, ToString.last_opt_target, tokens)

        return tokens

    def headline_ids(self):
        tokens = self._tokens
        msg = "%s %s %s" % (self.process_id(), self.partproc_id(), self.article())
        if len(tokens) >= 34 and tokens[33] == '1':
            msg += " is_started=1"
        return msg

    @classmethod
    def commands(cls):
        return ['DEF_ERPCommandcreate_Process______', ]

    def token_descriptions(self):
        if self.mode51():
            return ['process_area_head', 'process', 'part_process', 'part', 'part_variant', 'cro',
                'production_quantity', 'start_date', 'due_date', 'throughput_time_factor',
                'priority', 'earlyness_factor', 'transport_%',
                'matrix_%', 'waiting_time_%', 'mrp_area',
                '', # dummy for old Lagerort entry
                'is_head', 'free_quantity',
                'last_opt_type', 'last_opt_target', 'last_opt_time', 'lot', 'use_due_date',
                #'production_quantity_total',
                'BG_ueber_Lager', 'process_area', 'order_state']

        return ['process_area_head', 'process', 'part_process', 'part', 'part_variant', 'cro',
                'production_quantity', 'start_date', 'due_date', 'throughput_time_factor',
                'priority', 'earlyness_factor', 'transport_%',
                'matrix_%', 'waiting_time_%', 'mrp_area', 'is_head', 'free_quantity',
                'last_opt_type', 'last_opt_target', 'last_opt_time', 'lot', 'use_due_date',
                'production_quantity_total', 'BG_ueber_Lager', 'process_area', 'order_state', 'creation_date',
                'stability', 'age', 'preserve_dynamic_buffer', 'due_date_time', 'is_plant_order',
                'is_started']


class Coverage(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def process_id(self):
        """get id"""
        return self._tokens[1]

    def partproc_id(self):
        return int(self._tokens[2])

    def article(self):
        return self._tokens[3]

    def headline_ids(self):
        return "%s %s %s" % (self.process_id(), self.partproc_id(), self.article())

    @classmethod
    def commands(cls):
        return ['DEF_ERPCommandcreate_Coverage_____', ] # was create_ProcessProd

    def token_descriptions(self):
        if self.mode51():
            return []

        return ['process_area_head', 'process', 'part_process', 'part', 'part_variant', 'lot',
                'cro', 'reservation', 'mrp_area', 'Anzahl', 'ident_act', 'is_continuous']
