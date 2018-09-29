# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: tr_processcst_test.py
#
# description
"""\n\n
    Test TrProcessCst class
"""

import unittest
import message_file_reader
import os.path

class TrProcessCstTest(unittest.TestCase) :
    """test TrProcessCstTest class"""
    def setUp(self):
        self._target = self.get_test_constraint()
    
    def tearDown(self):
        pass
        
    def get_test_constraint(self):
        return self.get_test_constraints()[0]
    
    def get_test_constraints(self):
        testfile = os.path.join(os.path.dirname(__file__), 'testdata/lines_tr_processcst.txt')
        items = message_file_reader.read_message_file(testfile)
        return items

    def test_process_id_from(self):
        self.assertEqual('LA-14004813', self._target.process_id_from())
        
    def test_process_id_to(self):
        self.assertEqual('LA-14003194', self._target.process_id_to())
        
    def test_process_bereich_from(self):
        self.assertEqual('PPA', self._target.process_bereich_from())    
        
    def test_process_bereich_to(self):
        self.assertEqual('PPB', self._target.process_bereich_to())
     
    def test_next_akt_key(self):
        self.assertEqual('72806', self._target.next_akt_key())   
        
    def test_days_delay(self):
        self.assertEqual('1', self._target.days_delay())
    
    def test_line_with_description(self):
        line = self._target.line_with_description()
        self.assertNotEqual(line, '')           
