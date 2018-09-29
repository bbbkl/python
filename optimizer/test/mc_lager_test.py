# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: mc_lager_test.py
#
# description
"""\n\n
    Test McLager class
"""

import unittest
import message_file_reader
import os.path

class McLagerTest(unittest.TestCase) :
    """test McLager class"""
    def setUp(self):
        self._target = self.get_test_target()
    
    def tearDown(self):
        pass
        
    def get_test_target(self):
        return self.get_test_targets()[0]
    
    def get_test_targets(self):
        testfile = os.path.join(os.path.dirname(__file__), 'testdata/lines_mc_lager.txt')
        items = message_file_reader.read_message_file(testfile)
        return items

    def test_artikel(self):
        self.assertEqual('00301-641', self._target.artikel())
        
    def test_charge(self):
        self.assertEqual('00012911', self._target.charge())
        
    def test_lagerort(self):
        self.assertEqual('77', self._target.lagerort())    
        
    def test_bestand(self):
        self.assertEqual(19.0, self._target.bestand())
     
    def test_resbestand(self):
        self.assertEqual(0.0, self._target.resbestand())   
        
    def test_mrp_area(self):
        self.assertEqual('0', self._target.mrp_area())
        
    def test_line_with_description(self):
        line = self._target.line_with_description()
        self.assertNotEqual(line, '')           
