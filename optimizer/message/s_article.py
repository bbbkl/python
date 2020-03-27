# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: article.py
#
# description
"""\n\n
    Article class
    
    Ein S_Artikel
    hat ein oder mehrere MD_Artikel = (Dispobereich / mrp_area)
    ein MD_Artikel
    hat ein oder mehrere ML_Artort (Lagerorte)
    ein ML_Artort
    hat mehrere DispoBew 
"""

from message.baseitem import BaseItem
from to_string import ToString

class SArticle(BaseItem):
    """One Artikel"""
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)
        self._dispoparams = {} # dict mrp_area -> dispo_parameter
        self._ort = []
        self._dispo_bewegungen = []

    def __str__(self):
        text = "Artikel %s, Chargenart: %s, Artikelvariante: %s, Kommissionslager: %s, WBZ: %d, WBZ_Überlast: %d" %\
            (self.article_id(), self.chargenart(), self.art_var_typ(), self.kommissionslager(), self.wbz(), self.wbz_overload())
        for item in self._dispoparams.values():
            text += "\n\tDP %s" % item
        for item in self._ort:
            text += "\n\tOrt %s" % item
        for item in self._dispo_bewegungen:
            text += "\n\tBew %s" % item
        return text

    def article_id(self):
        """get id"""
        return self._tokens[0]

    def chargenart(self):
        return self._tokens[1]

    def art_var_typ(self):
        """Artikelvariante"""
        return self._tokens[2]

    def kommissionslager(self):
        return self._tokens[3]

    def wbz(self):
        return int(self._tokens[4])

    def wbz_overload(self):
        return int(self._tokens[5])

    def floatingpoint_multiplier(self):
        pos = 6
        if len(self._tokens) > pos:
            return pow(10, int(self._tokens[pos]))
        return 100 # default

    def dispo_parameter(self, mrp_area):
        if mrp_area in self._dispoparams:
            return self._dispoparams[mrp_area]
        return None

    def add_dispo_parameter(self, dispo_parameter):
        key = dispo_parameter.mrp_area()
        self._dispoparams[key] = dispo_parameter

    def add_ort(self, ort):
        self._ort.append(ort)

    def add_dispobew(self, dispobew):
        self._dispo_bewegungen.append(dispobew)

    def verbose_tokens(self):
        """possibility to enrich some cryptic values with their human readable description"""
        tokens = list(self._tokens)
        self.verbose_token(3, ToString.kommlager, tokens)
        return tokens

    def headline_ids(self):
        return "%s %s %s %s" % (self.article_id(), self.chargenart(), self.art_var_typ(), self.kommissionslager())

    @classmethod
    def commands(cls):
        return ['DEF_ERPCommandcreate_S_Artikel____',]

    def token_descriptions(self):
        if self.mode51():
            return ['part', 'Chargenart', 'Art_Variante', 'Komm_Lager',
                    'WBZ', # differnce to 5.3
                    'WBZ_Ovl', 'Nachkommastellen']
        return ['part', 'Chargenart', 'Art_var_typ', 'Komm_Lager',
                'wbz_ovl_default', 'Nachkommastellen']
