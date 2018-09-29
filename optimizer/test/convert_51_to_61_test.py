# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: convert_51_to_61_test.py
#
# description
"""\n\n
    Test conversion 51 to 61
"""
import unittest
import os.path
from message.m_resource import *

class Conversion51To61Test(unittest.TestCase):

    def get_dataline(self, target_name):
        testfile = os.path.join(os.path.dirname(__file__), 'testdata/lines_%s.51.txt' % target_name)
        return open(testfile).readline()

    def test_convert_M_Resource(self):
        #dataline51 = '3    4    2511    3_LFO        100    1    2    0    0        0    2    0'
        dataline51 = self.get_dataline('m_resource')
        command = None
        BaseItem.set_mode51(True)
        tokens = dataline51.split('\t')
        m_resource = M_Resource(tokens, command)
        tokens_converted = m_resource.convert_to_61()
        BaseItem.set_mode51(False)
        m_resource61 = M_Resource(tokens_converted, command)
        self.assertEqual('', m_resource61.get_token(tokens_converted, 'buffer_time'))
        self.assertEqual('', m_resource61.get_token(tokens_converted, 'Pufferzeiteinheit'))
        self.assertEqual('0', m_resource61.get_token(tokens_converted, 'SetupRvt'))
        self.assertEqual('0', m_resource61.get_token(tokens_converted, 'IntIgn'))
        self.assertEqual(m_resource61.get_token(tokens_converted, 'intensity'), m_resource61.get_token(tokens_converted, 'IntOvl'))
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()