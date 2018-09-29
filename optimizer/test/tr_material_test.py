# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: material_test.py
#
# description
"""\n\n
    Test Material class
"""

import unittest
import message_file_reader
import os.path

class TrMaterialTest(unittest.TestCase) :
    def setUp(self):
        # 3    PPA    LA-00000006    6    10    10    0013838        30    37    0        PPA    6|8        30    0
        self._target = self.getTestTarget()
    
    def tearDown(self):
        pass
        
    def getTestTarget(self):
        return self.getTestTargets()[0]
    def getTestTargets(self):
        testfile = os.path.join(os.path.dirname(__file__), 'testdata/lines_tr_material.txt')
        return message_file_reader.read_message_file(testfile)

    def test_process_id(self):
        self.assertEqual('LA-00000006', self._target.process_id())
    
    def test_line_with_description(self):
        line = self._target.line_with_description()
        self.assertNotEqual(line, '')
