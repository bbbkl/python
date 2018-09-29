# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: m_serverkennz.py
#
# description
"""\n\n
    MServerKennz class
"""

from message.baseitem import BaseItem

class MServerKennz(BaseItem):
    """One MServerKennz"""
    def __init__(self, tokens, command):
        BaseItem.__init__(self, tokens, command)

    @classmethod
    def commands(cls):
        return ['DEF_APSCommandcreate_M_ServerKennZ', ]

    def token_descriptions(self):
        return ['GlobDurchLaufzeitFakt', 'GlobKapAuslastFakt', 'GlobGewichtungVerfr', 'GlobGewichtungVersp',
                'LocDurchLaufzeitFakt', 'LocGewichtungVerfr', 'LocKapAuslastFakt', 'LocGewichtungVersp', 'StartTermin',
                'StartZeit', 'Dauer', 'MittlereVerspaetung', 'MittlereVerfruehung', 'MittlereDLZ',
                'MaxVerspaetung', 'MaxVerfruehung', 'MaxDLZ', 'AnzahlAktivitaetenERP', 'AnzahlAktivitaetenINT',
                'AnzahlAktivitaetenFIX', 'AnzahlArtikel', 'AnzahlArtikelZuordnung', 'AnzahlRess', 'AnzahlRessZuordnung',
                'AnzahlAuftraege', 'AnzahlProblemAuftraege', 'Verspaehtet', 'Verfrueht', 'Ueberlastet',
                'Blockgroesse', 'AnzahlBloecke', 'BloeckeMitLoesung', 'Optimierungsnummer',
                '#Baugruppen', '#BaugruppenMitWT', '#BaugruppenMitWT_verspaetet' ]