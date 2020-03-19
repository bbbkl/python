# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: ort.py
#
# description
"""\n\n
    ML_ArtOrt class
"""

from message.baseitem import BaseItem

class ML_ArtOrt(BaseItem):
    """store or place of an article"""
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def __str__(self):
        text = "bestand: %d, lagerort: %s, mrp_area: %s" % \
            (self.bestand(), self.lagerort(), self.mrp_area())
        return text

    def article_id(self):
        """get id"""
        return self._tokens[0]

    def bestand(self):
        return self.to_float(self._tokens[1])

    def sicherheitsbestand(self):
        return self.to_float(self._tokens[2])

    def res_bestand(self):
        return self.to_float(self._tokens[3])

    def kommissions_bestand(self):
        return self.to_float(self._tokens[4])

    def lagerort(self):
        return self._tokens[5]

    def mrp_area(self):
        if len(self._tokens) > 6:
            return self._tokens[6]
        return "-1"

    def key_main(self):
        return "%s_%s_%s" % (self.article_id(), self.lagerort(), self.mrp_area())

    @classmethod
    def commands(cls):
        return ['DEF_ERPCommandcreate_ML_Artort____', ]

    def token_descriptions(self):
        return ['ArtId', 'Bestand', 'SBestand', 'Res_b', 'Kom_b', 'LOrt', 'mrp_area', 'reservation']
