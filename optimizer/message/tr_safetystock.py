# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: tr_safetystock.py
#
# description
"""\n\n
    TrSafetyStock class
"""

from message.baseitem import BaseItem

class TrSafetyStock(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    @classmethod
    def commands(cls):
        return ['DEF_ERPCommandcreate_ApsTrSafetySt', ]

    def token_descriptions(self):
        return ['part', 'part_variant', 'mrp_area', 'safety_stock', 'priority']
