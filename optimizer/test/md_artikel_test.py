# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: article_test.py
#
# description
"""\n\n
    Test Article class
"""

import unittest
import message_file_reader
import os.path

class MD_ArtikelTest(unittest.TestCase) :
    """test DispoParameter class"""
    def setUp(self):
        # 3    42416104   0    1    0     0    80    3    0      3    0      0    
        # 3    6000301    0    1    50    0    12    4    100    4    100    0
        self._target = self.getTestTarget()
    
    def tearDown(self):
        pass
        
    def getTestTarget(self):
        testfile = os.path.join(os.path.dirname(__file__), 'testdata/lines_md_artikel.txt')
        items = message_file_reader.read_message_file(testfile)
        return items[0]

    def test_article_id(self):
        self.assertEqual('6000301', self._target.article_id())
        
    def test_mrp_area(self):
        self.assertEqual('0', self._target.mrp_area())
        
    def test_vorlaufzeit(self):
        self.assertEqual(1, self._target.vorlaufzeit())
        
    def test_prod_lager_zu(self):
        self.assertEqual('50', self._target.prod_lager_zu())
        
    def test_kontinuierlich(self):
        self.assertEqual(False, self._target.kontinuierlich())
        
    def test_wbz(self):
        self.assertEqual(12, self._target.wbz())
        
    def test_zeiteinheit_wbz(self):
        self.assertEqual(4, self._target.zeiteinheit_wbz())
    
    def test_workingday_company_calendar_wbz(self):
        self.assertEqual(100, self._target.workingday_company_calendar_wbz())
        
    def test_zeiteinheit_wbz_overload(self):
        self.assertEqual(4, self._target.zeiteinheit_wbz_overload())
        
    def test_workingday_company_calendar_wbz_overload(self):
        self.assertEqual(100, self._target.workingday_company_calendar_wbz_overload())
        
    def test_transportzeit(self):
        self.assertEqual(0, self._target.transportzeit())
        
    def test_zeiteinheit_transportzeit(self):
        self.assertEqual(0, self._target.zeiteinheit_transportzeit())
        
    def test_line_with_description(self):
        line = self._target.line_with_description()
        self.assertNotEqual(line, '')   
        
    
