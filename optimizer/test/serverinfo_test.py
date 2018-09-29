# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: serverinof_test.py
#
# description
"""\n\n
    Test ServerInfo class
"""
import unittest
import message_file_reader
import datetime
import os.path

class ServerInfoTest(unittest.TestCase):
    """test ServerInfo class"""
    def setUp(self):
        # 3    17.02.2012    11:22    ,8    ,1    0    1    M    -1    120    1    ,1    22
        self._target = self.get_test_target()
    
    def tearDown(self):
        pass

    def testName(self):
        return "ServerInfoTest"
    
    def get_test_target(self):
        testfile = os.path.join(os.path.dirname(__file__), 'testdata/lines_server.txt')
        items = message_file_reader.read_message_file(testfile)
        return items[0]
    
    def test_time(self):
        # 17.02.2012    11:22
        expected = datetime.datetime(2012, 2, 17, 11, 22)
        self.assertEqual(expected, self._target.time())
        
    def test_server_time_interval(self):
        self.assertEqual('minutes', self._target.server_time_interval())

    def test_line_with_description(self):
        line = self._target.line_with_description()
        self.assertNotEqual(line, '')
        
class ZeitMengenEinheitTest(unittest.TestCase):
    
    def setUp(self):
        # 3    3    1000
        self._target = self.get_test_target()
        
    def tearDown(self):
        pass
    
    def get_test_target(self):
        return self.get_test_targets()[0]
    def get_test_targets(self):
        testfile = os.path.join(os.path.dirname(__file__), 'testdata/lines_zeitmengeneinheit.txt')
        return message_file_reader.read_message_file(testfile)

    def test_zeitmengeneinheit(self):
        self.assertEqual(3, self._target.zeitmengeneinheit())
    
    def factor(self):
        self.assertEqual(1000.0, self._target.factor())

    def test_line_with_description(self):
        line = self._target.line_with_description()
        self.assertNotEqual(line, '')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
