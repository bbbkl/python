# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: article.py
#
# description
"""\n\n
    Article class
"""

from message.baseitem import BaseItem
from to_string import ToString

class MD_Artikel(BaseItem):
    """Dispoparameter für einen Artikel"""
    # 3    6000301    0    1    50    0    12    4    100    4    100    0
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def __str__(self):
        text = "Dispoparameter Artikel %s, mrp_area: %s, Vorlaufzeit: %d, Prodlagerzu: %s, Kontinuierlich: %s, WBZ: %d, cal: %d, calÜberlast: %d" % \
            (self.article_id(), self.mrp_area(), self.vorlaufzeit(), self.prod_lager_zu(), self.kontinuierlich(), self.wbz(),
             self.workingday_company_calendar_wbz(), self.workingday_company_calendar_wbz_overload())
        return text

    def article_id(self):
        """get part id"""
        return self._tokens[0]

    def mrp_area(self):
        return self._tokens[1]

    def vorlaufzeit(self):
        return int(self._tokens[2])

    def prod_lager_zu(self):
        return self._tokens[3]

    def kontinuierlich(self):
        return self._tokens[4] != '0'

    def wbz(self):
        return int(self._tokens[5])

    def zeiteinheit_wbz(self):
        return int(self._tokens[6])

    def workingday_company_calendar_wbz(self):
        return int(self._tokens[7])

    def zeiteinheit_wbz_overload(self):
        return int(self._tokens[8])

    def workingday_company_calendar_wbz_overload(self):
        return int(self._tokens[9])

    def transportzeit(self):
        return int(self._tokens[10])

    def zeiteinheit_transportzeit(self):
        val = self._tokens[11]
        if val:
            return int(val)
        return 0

    def headline_ids(self):
        return "%s %s" % (self.article_id(), self.mrp_area())

    @classmethod
    def commands(cls):
        return ['DEF_ERPCommandcreate_MD_Artikel___',]

    def verbose_tokens(self):
        """possibility to enrich some cryptic values with their human readable description"""
        tokens = list(self._tokens)
        self.verbose_token(6, ToString.time_unit, tokens)
        self.verbose_token(8, ToString.time_unit, tokens)
        self.verbose_token(11, ToString.time_unit, tokens)
        self.verbose_token(14, ToString.time_unit, tokens)
        return tokens

    def token_descriptions(self):
        descriptions = ['part', 'mrp_area', 'Vorlaufzeit', 'Prod_Lager_zu', 'continious',
                'wbz', 'wbz_timeunit', 'wbz_company_cal', 'wbz_timeunit_ovl', 'wbz_company_cal_ovl',
                'transport_time', 'transport_timeunit', 'use_calendar_for_forerun(3=true)',
                'mrp_horizon', 'mrp_horizon_timeunit',
                'dynamic_replenishment_time', 'advance_coverages', 'wbz_ovl']

        return descriptions
