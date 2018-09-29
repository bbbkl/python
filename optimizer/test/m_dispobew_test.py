# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: dispobew_test.py
#
# description
"""\n\n
    Test Bestandskurve class
"""

import unittest
import message_file_reader
import os.path

class M_DispoBewTest(unittest.TestCase) :
    """test DispoBew class"""
    def setUp(self):
        # 3    0013838        05.05.2012    0    50    0    MDD    27    00:00    0    0        0
        self._target = self.getTestTarget()
    
    def tearDown(self):
        pass
        
    def getTestTarget(self):
        testfile = os.path.join(os.path.dirname(__file__), 'testdata/lines_m_dispobew.txt')
        items = message_file_reader.read_message_file(testfile)
        return items[0]

    def test_article_id(self):
        self.assertEqual('0013838', self._target.article_id())
        
    def test_art_var(self):
        self.assertEqual('', self._target.art_var())

    def test_dispo_termin(self):
        self.assertEqual('05.05.2012', self._target.dispo_termin())
    
    def test_bedarfsmenge(self):
        self.assertEqual(0.0, self._target.bedarfsmenge())
    
    def test_deckungsmenge(self):
        self.assertEqual(50.0, self._target.deckungsmenge())
    
    def test_reservierungsmenge(self):
        self.assertEqual(0.0, self._target.reservierungsmenge())
    
    def test_belegart_herkunft(self):
        self.assertEqual('MDD', self._target.belegart_herkunft())
    
    def test_schl_herkunft(self):
        self.assertEqual('27', self._target.schl_herkunft())
    
    def test_dispo_time(self):
        self.assertEqual('00:00', self._target.dispo_time())
    
    def test_kommision(self):
        self.assertEqual(0, self._target.kommision())
    
    def test_mrp_area(self):
        self.assertEqual('0', self._target.mrp_area())
        
    def test_charge(self):
        self.assertEqual('', self._target.charge())
        
    def test_is_active_order(self):
        self.assertEqual(False, self._target.is_active_order())
    
    def test_line_with_description(self):
        line = self._target.line_with_description()
        self.assertNotEqual(line, '')
