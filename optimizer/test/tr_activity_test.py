# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: activity_test.py
#
# description
"""\n\n
    Test Activity class
"""

import unittest
import datetime
import message_file_reader
import os.path

class TrActivityTest(unittest.TestCase) :
    """test Activity class"""
    def setUp(self):
        # 3    PPA    2N-11400889-0010    11223694    2    0    7823935    1    0    1    2200    0    1    1    1    13.12.2011    14.12.2011    0    20.10.2011    0    20.10.2011    14940    65940    0    1    0    1    0    1    1    0    0        0    10    2200    0    0    0    PPA
        self._target = self.get_test_activity()
    
    def tearDown(self):
        pass
        
    def get_test_activity(self):
        return self.get_test_activities()[0]
    
    def get_test_activities(self):
        testfile = os.path.join(os.path.dirname(__file__), 'testdata/lines_tr_activity.txt')
        items = message_file_reader.read_message_file(testfile)
        return items

    def test_process_id(self):
        self.assertEqual('2N-11400889-0010', self._target.process_id())
        
    def test_process_bereich(self):
        self.assertEqual('PPA', self._target.process_bereich())
        
    def test_process_bereich_orig(self):
        self.assertEqual('PPA', self._target.process_bereich_orig())    
        
    def test_partproc_id(self):
        self.assertEqual('11223694', self._target.partproc_id())
     
    def test_act_art(self):
        self.assertEqual('Produktion', self._target.act_art())   
        
    def test_ident_akt(self):
        self.assertEqual('7823935', self._target.ident_akt())
        
    def test_start_time(self):
        expected = datetime.datetime(2011, 12, 13, 4, 9)
        self.assertEqual(expected, self._target.start_time())
        
    def test_end_time(self):
        expected = datetime.datetime(2011, 12, 14, 18, 19)
        self.assertEqual(expected, self._target.end_time())
        
    def test_tr(self):
        self.assertEqual(2200.0, self._target.tr())

    def test_te(self):
        self.assertEqual(0.0, self._target.te())
        
    def test_zeitmengeneinheit(self):
        self.assertEqual(1, self._target.zeitmengeneinheit())   
        
    def test_fixiert(self):
        self.assertFalse(self._target.fixiert())
    
    def test_zeitraum_einheit(self):
        self.assertEqual(1, self._target.zeitraum_einheit())
    
    def test_done(self):
        self.assertFalse(self._target.done())
    
    def test_line_with_description(self):
        line = self._target.line_with_description()
        self.assertNotEqual(line, '')           
