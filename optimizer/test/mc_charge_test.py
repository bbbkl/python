# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: mc_charge_test.py
#
# description
"""\n\n
    Test McCharge class
"""

import unittest
import message_file_reader
import os.path

class McChargeTest(unittest.TestCase) :
    """test McCharge class"""
    def setUp(self):
        self._target = self.get_test_target()
    
    def tearDown(self):
        pass
        
    def get_test_target(self):
        return self.get_test_targets()[0]
    
    def get_test_targets(self):
        testfile = os.path.join(os.path.dirname(__file__), 'testdata/lines_mc_charge.txt')
        items = message_file_reader.read_message_file(testfile)
        return items

    def test_artikel(self):
        self.assertEqual('00301-641', self._target.artikel())
        
    def test_charge(self):
        self.assertEqual('00003923', self._target.charge())
        
    def test_verfallsdatum(self):
        self.assertEqual('20.01.2012', self._target.verfallsdatum())    
        
    def test_line_with_description(self):
        line = self._target.line_with_description()
        self.assertNotEqual(line, '')           
