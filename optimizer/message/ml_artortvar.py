# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: ort.py
#
# description
"""\n\n
    ML_ArtOrtVar class
"""

from message.baseitem import BaseItem

class ML_ArtOrtVar(BaseItem):
    """store or place of an article with a variant"""
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)
        
    def __str__(self):
        text = "bestand: %d, ArtVar: %s lagerort: %s, mrp_area: %s" % \
            (self.bestand(), self.artvar(), self.lagerort(), self.mrp_area())
        return text
    
    def article_id(self):
        """get id"""
        return self._tokens[0]
    
    def artvar(self):
        """get artvar"""
        return self._tokens[1]
    
    def bestand(self):
        return self.to_float(self._tokens[2])
    
    def sicherheitsbestand(self):
        return self.to_float(self._tokens[3])
    
    def res_bestand(self):
        return self.to_float(self._tokens[4])
    
    def lagerort(self):
        return self._tokens[5]
    
    def mrp_area(self):
        if len(self._tokens) > 6:
            return self._tokens[6]
        return "-1"

    def key_main(self):
        return "%s_%s_%s_%s" % (self.article_id(), self.artvar(), self.lagerort(), self.mrp_area)
    
    @classmethod        
    def commands(cls):
        return ['DEF_ERPCommandcreate_ML_Artortvar_', ]
    
    def token_descriptions(self):
        return ['ArtID', 'part_variant', 'Bestand', 'SBestand', 'Res_b', 'LOrt', 'LGruppe', 
                'reservation']
