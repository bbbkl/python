# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: calendar_test.py
#
# description
"""\n\n
    Test Calendar class
"""

import unittest
import message_file_reader
import os.path

class S_BetriebKalTest(unittest.TestCase) :
    def setUp(self):
        self._target = self.getTestTarget()
    
    def tearDown(self):
        pass
        
    def getTestTarget(self):
        return self.getTestTargets()[0]
    def getTestTargets(self):
        testfile = os.path.join(os.path.dirname(__file__), 'testdata/lines_calendar.txt')
        return message_file_reader.read_message_file(testfile)
            
    def test_line_with_description(self):
        line = self._target.line_with_description()
        self.assertNotEqual(line, '')            
            
class M_KalendarTest(unittest.TestCase):
    def setUp(self):
        self._target = self.getTestTarget()
        
    def tearDown(self):
        pass
    
    def getTestTarget(self):
        return self.getTestTargets()[0]
    def getTestTargets(self):
        testfile = os.path.join(os.path.dirname(__file__), 'testdata/lines_m_calendar.txt')
        return message_file_reader.read_message_file(testfile)
    
    def test_line_with_description(self):
        line = self._target.line_with_description()
        self.assertNotEqual(line, '')
        
class M_KalendarZeitTest(unittest.TestCase):
    def setUp(self):
        self._target = self.getTestTarget()
        
    def tearDown(self):
        pass
    
    def getTestTarget(self):
        return self.getTestTargets()[0]
    def getTestTargets(self):
        testfile = os.path.join(os.path.dirname(__file__), 'testdata/lines_m_kalenderzeit.txt')
        return message_file_reader.read_message_file(testfile)
    
    def test_line_with_description(self):
        line = self._target.line_with_description()
        self.assertNotEqual(line, '')
        
class M_IntKalenderTest(unittest.TestCase):
    def setUp(self):
        self._target = self.getTestTarget()
        
    def tearDown(self):
        pass
    
    def getTestTarget(self):
        return self.getTestTargets()[0]
    def getTestTargets(self):
        testfile = os.path.join(os.path.dirname(__file__), 'testdata/lines_m_intkalender.txt')
        return message_file_reader.read_message_file(testfile)
    
    def test_line_with_description(self):
        line = self._target.line_with_description()
        self.assertNotEqual(line, '')