# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: resource_test.py
#
# description
"""\n\n
    Test Resource class
"""

import unittest
import message_file_reader
import os.path

class TrResourceTest(unittest.TestCase) :
    def setUp(self):
        # 3    CDD    CDD-80211990    98    10    0    7    11101    4779    1    0    1        0
        # 3    7    M000    820    IMPORT    0    1    2    0    0        0        0    0    0
        self._target = self.get_test_target()
    
    def tearDown(self):
        pass
        
    def get_test_target(self):
        return self.get_test_targets()[0]
    def get_test_targets(self):
        testfile = os.path.join(os.path.dirname(__file__), 'testdata/lines_tr_resource.txt')
        return message_file_reader.read_message_file(testfile)

    def test_process_id(self):
        self.assertEqual('CDD-80211990', self._target.process_id())
        
    def test_prozessbereich(self):    
        self.assertEqual('CDD', self._target.prozessbereich())
        
    def test_teilprozess(self):
        self.assertEqual('98', self._target.teilprozess())
        
    def test_akt_pos(self):
        self.assertEqual('10', self._target.akt_pos())
    
    def test_res_pos(self):
        self.assertEqual('0', self._target.res_pos())    
        
    def test_ident_akt(self):
        self.assertEqual('4779', self._target.ident_akt())    
        
    def test_intensity(self):
        self.assertEqual(1.0, self._target.intensity())
        
    def test_use_alt_group(self):
        self.assertFalse(self._target.use_alt_group())  
        
    def test_is_basis_resource(self):
        self.assertTrue(self._target.is_basis_resource())
        
    def test_res_art(self):
        self.assertEqual(7, self._target.res_art())
        
    def test_resource(self):
        self.assertEqual('11101', self._target.resource())
        
    def test_activity_key(self):
        self.assertEqual('CDD_CDD-80211990_98_4779', self._target.activity_key())

    def test_line_with_description(self):
        line = self._target.line_with_description()
        self.assertNotEqual(line, '')