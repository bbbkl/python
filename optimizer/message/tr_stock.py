# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: tr_stock.py
#
# description
"""\n\n
    TrStock class
"""

from message.baseitem import BaseItem

class TrStock(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    @classmethod
    def commands(cls):
        return ['DEF_ERPCommandcreate_ApsTrStock___', ]

    def token_descriptions(self):
        return ['part', 'part_variant', 'lot', 'cro', 'reservation',
                'mrp_area', 'stock' ]

class TrStockFromMLArtOrtKomm(BaseItem):
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    @classmethod
    def commands(cls):
        return ['DEF_ERPCommandcreate_ML_Artortkomm', ]

    def token_descriptions(self):
        return ['part', 'cro', 'stock', '<unused>', 'part_variant',
                'mrp_area', 'reservation' ]
