# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: dispobew.py
#
# description
"""\n\n
    Bestandskurve class
"""

from message.baseitem import BaseItem

class M_DispoBew(BaseItem):
    """store or place of an article"""
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    def __str__(self):
        text = "termin: %s, bedarfsmenge: %d, deckungsmenge: %d, mrp_area: %s" % \
            (self.dispo_termin(), self.bedarfsmenge(), self.deckungsmenge(), self.mrp_area())
        return text

    def article_id(self):
        """get id"""
        return self._tokens[0]

    def art_var(self):
        return self._tokens[1]

    def dispo_termin(self):
        return self._tokens[2]

    def bedarfsmenge(self):
        return self.to_float(self._tokens[3])

    def deckungsmenge(self):
        return self.to_float(self._tokens[4])

    def reservierungsmenge(self):
        return self.to_float(self._tokens[5])

    def belegart_herkunft(self):
        return self._tokens[6]

    def schl_herkunft(self):
        return self._tokens[7]

    def dispo_time(self):
        return self._tokens[8]

    def kommision(self):
        return int(self._tokens[9])

    def mrp_area(self):
        return self._tokens[10]

    def charge(self):
        return self._tokens[11]

    def is_active_order(self):
        return  self._tokens[12] == '1'

    def headline_ids(self):
        amount = self.deckungsmenge()
        if amount == 0.0:
            amount = -1.0 * self.bedarfsmenge()
        return "%s %s %s %2.1f %s" % (self.article_id(), self.mrp_area(), self.dispo_termin(),
                                      amount, self.belegart_herkunft())

    @classmethod
    def commands(cls):
        return ['DEF_ERPCommandcreate_M_DispoBew___', 'DEF_ERPCommandcreate_ApsTrMRPMovem']

    def token_descriptions(self):
        if self.mode51():
            return ['ArtId', 'part_variant', 'Dispotermin', 'demand_quantity', 'Deckungsmenge',
                'Reservierungsmenge', 'Belegart_herkunft', 'Schl_herkunft', 'Dispozeit',
                'cro', 'mrp_area',
                'Lagerort', # diff to 5.3
                'lot', 'Active_order']
        return ['ArtId', 'part_variant', 'Dispotermin', 'demand_quantity', 'Deckungsmenge',
                'Reservierungsmenge', 'Belegart_herkunft', 'Schl_herkunft', 'Dispozeit',
                'cro', 'mrp_area', 'lot', 'Active_order', 'reservation',
                'trigger_coverage_scheduling', 'priority', 'age', 'part_process']
