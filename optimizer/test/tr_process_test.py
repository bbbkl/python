# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: process_test.py
#
# description
"""\n\n
    Test TrProcess class
"""

import unittest
import message_file_reader
import os.path

class TrProcessTest(unittest.TestCase) :
    def setUp(self):
        # 3    PPA    A-00011023-0010    16    ZYLINDER_TA4        11023    1    02.10.2012    15.07.2012    ,1    1,000122    ,1    100    100    100    0    1    0    0    0    15.03.2012        1    1    0    PPA
        self._target = self.getTestTarget()
    
    def tearDown(self):
        pass
        
    def getTestTarget(self):
        return self.getTestTargets()[0]
    def getTestTargets(self):
        testfile = os.path.join(os.path.dirname(__file__), 'testdata/lines_tr_process.txt')
        return message_file_reader.read_message_file(testfile)

    def test_process_bereich(self):    
        self.assertEqual('PPA', self._target.process_bereich())

    def test_process_id(self):
        self.assertEqual('A-00011023-0010', self._target.process_id())
    
    def test_article(self):
        self.assertEqual('ZYLINDER_TA4', self._target.article())  
        
    def test_partproc_id(self):
        self.assertEqual(16, self._target.partproc_id())  
        
    def test_quantity(self):
        self.assertEqual(1.0, self._target.quantity())
        
    def test_is_head(self):
        self.assertTrue(self._target.is_head())
        
    def test_process_bereich_orig(self):
        self.assertEqual('PPA', self._target.process_bereich_orig())
    
    def test_line_with_description(self):
        line = self._target.line_with_description()
        self.assertNotEqual(line, '')
