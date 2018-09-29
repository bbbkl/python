# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: mc_uebort_test.py
#
# description
"""\n\n
    Test M_UebOrt class
"""

import unittest
import message_file_reader
import os.path

class M_UebOrtTest(unittest.TestCase) :
    """test M_UebOrt class"""
    def setUp(self):
        self._target = self.get_test_target()
    
    def tearDown(self):
        pass
        
    def get_test_target(self):
        return self.get_test_targets()[0]
    
    def get_test_targets(self):
        testfile = os.path.join(os.path.dirname(__file__), 'testdata/lines_m_uebort.txt')
        items = message_file_reader.read_message_file(testfile)
        return items

    def test_adressnr(self):
        self.assertEqual('4', self._target.adressnr())

    def test_von_ort(self):
        self.assertEqual('BOHREN', self._target.von_ort())
        
    def test_nach_ort(self):
        self.assertEqual('SCHWEIßEN', self._target.nach_ort())   
        
    def test_transition_time(self):
        self.assertEqual(45, self._target.transition_time())   
    
    def test_transition_time_unit(self):
        self.assertEqual(1, self._target.transition_time_unit())   
        
    def test_dynamic_buffer_time(self):
        self.assertEqual(77, self._target.dynamic_buffer_time())   
    
    def test_dynamic_buffer_time_unit(self):
        self.assertEqual(7, self._target.dynamic_buffer_time_unit())         
        
    def test_line_with_description(self):
        line = self._target.line_with_description()
        self.assertNotEqual(line, '')           
