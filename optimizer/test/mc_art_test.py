# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: mc_art_test.py
#
# description
"""\n\n
    Test McArt class
"""

import unittest
import message_file_reader
import os.path

class McArtTest(unittest.TestCase) :
    """test McArt class"""
    def setUp(self):
        self._target = self.get_test_target()
    
    def tearDown(self):
        pass
        
    def get_test_target(self):
        return self.get_test_targets()[0]
    
    def get_test_targets(self):
        testfile = os.path.join(os.path.dirname(__file__), 'testdata/lines_mc_art.txt')
        items = message_file_reader.read_message_file(testfile)
        return items

    def test_chargenart(self):
        self.assertEqual('1', self._target.chargenart())

    def test_fertigungsmix(self):
        self.assertEqual('1', self._target.fertigungsmix())
        
    def test_verfallsdatum(self):
        self.assertEqual('0', self._target.verfallsdatum())    
        
    def test_line_with_description(self):
        line = self._target.line_with_description()
        self.assertNotEqual(line, '')           
