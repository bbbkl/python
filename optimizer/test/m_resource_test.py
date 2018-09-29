# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: m_resource_test.py
#
# description
"""\n\n
    Test M_Resource class
"""

import unittest
import message_file_reader
import os.path

class M_ResourceTest(unittest.TestCase) :
    def setUp(self):
        # 3    7    19106    10    10    100    1    2    0    1    KUNSTST_M1    0    2    ,1    0    0    0
        self._target = self.get_test_target()
    
    def tearDown(self):
        pass
        
    def get_test_target(self):
        return self.get_test_targets()[0]
    def get_test_targets(self):
        testfile = os.path.join(os.path.dirname(__file__), 'testdata/lines_m_resource.txt')
        return message_file_reader.read_message_file(testfile)

    def test_res_art(self):
        self.assertEqual(7, self._target.res_art())
        
    def test_resource(self):    
        self.assertEqual('19106', self._target.resource())
        
    def test_resource_group(self):
        self.assertEqual('10', self._target.resource_group())
        
    def test_calendar(self):
        self.assertEqual('10', self._target.calendar())
    
    def test_belastungsgrenze(self):
        self.assertEqual(100, self._target.belastungsgrenze())    
        
    def test_intensity(self):
        self.assertEqual(1.0, self._target.intensity())    
        
    def test_is_engpass(self):
        self.assertFalse(self._target.is_engpass())   
    
    def test_is_ueberlast_ok(self):
        self.assertTrue(self._target.is_ueberlast_ok())
        
    def test_place(self):
        self.assertEqual('KUNSTST_M1', self._target.place())
        
    def test_waiting_time(self):
        self.assertEqual(0.0, self._target.waiting_time())
        
    def test_timeunit(self):
        self.assertEqual(2, self._target.timeunit())
        
    def test_weightfactor(self):    
        self.assertEqual(0.1, self._target.weightfactor())
        
    def test_is_setup_relevant(self):
        self.assertFalse(self._target.is_setup_relevant())
        
    def test_overload_intensity(self):
        self.assertEqual(0, self._target.overload_intensity())
    
    def test_ignore_intensity(self):
        self.assertFalse(self._target.ignore_intensity())
        
    def test_line_with_description(self):
        line = self._target.line_with_description()
        self.assertNotEqual(line, '')
        
class M_ResAltTest(unittest.TestCase) :
    def setUp(self):
        # 3    7    30    13101    0
        self._target = self.get_test_target()
    
    def tearDown(self):
        pass
        
    def get_test_target(self):
        return self.get_test_targets()[0]
    def get_test_targets(self):
        return message_file_reader.read_message_file("test/testdata/lines_m_resalt.txt")

    def test_res_art(self):
        self.assertEqual('7', self._target.res_art())
        
    def test_alt_group(self):    
        self.assertEqual('30', self._target.alt_group())
        
    def test_resource(self):    
        self.assertEqual('13101', self._target.resource())
        
    def test_priority(self):
        self.assertEqual('0', self._target.priority())   
    
    def test_line_with_description(self):
        line = self._target.line_with_description()
        self.assertNotEqual(line, '')     
        
class M_ResAltGroupTest(unittest.TestCase) :
    def setUp(self):
        # 3    7    10
        self._target = self.get_test_target()
    
    def tearDown(self):
        pass
        
    def get_test_target(self):
        return self.get_test_targets()[0]
    def get_test_targets(self):
        return message_file_reader.read_message_file("test/testdata/lines_m_resaltgroup.txt")

    def test_res_art(self):
        self.assertEqual('7', self._target.res_art())
        
    def test_alt_group(self):    
        self.assertEqual('10', self._target.alt_group())
    
    def test_line_with_description(self):
        line = self._target.line_with_description()
        self.assertNotEqual(line, '')  
