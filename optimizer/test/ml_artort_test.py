# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: ort_test.py
#
# description
"""\n\n
    Test Ort class
"""

import unittest
import message_file_reader
import os.path

class ML_ArtOrtTest(unittest.TestCase) :
    """test ML_ArtOrt class"""
    def setUp(self):
        # 3    0013838    40    0    1    2    -1    0
        self._target = self.getTestTarget()
    
    def tearDown(self):
        pass
        
    def getTestTarget(self):
        testfile = os.path.join(os.path.dirname(__file__), 'testdata/lines_ml_artort.txt')
        items = message_file_reader.read_message_file(testfile)
        return items[0]

    def test_article_id(self):
        self.assertEqual('0013838', self._target.article_id())
        
    def test_bestand(self):
        self.assertEqual(40.0, self._target.bestand())
    
    def test_sicherheitsbestand(self):
        self.assertEqual(0.0, self._target.sicherheitsbestand())
    
    def test_res_bestand(self):
        self.assertEqual(1.0, self._target.res_bestand())
    
    def test_kommissions_bestand(self):
        self.assertEqual(2.0, self._target.kommissions_bestand())
    
    def test_lagerort(self):
        self.assertEqual('-1', self._target.lagerort())
    
    def test_mrp_area(self):
        self.assertEqual('0', self._target.mrp_area())
        
    def test_line_with_description(self):
        line = self._target.line_with_description()
        self.assertNotEqual(line, '')
