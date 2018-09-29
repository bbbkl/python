# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: m_ressgruppe_test.py
#
# description
"""\n\n
    Test MRessGruppe class
"""

import unittest
import message_file_reader
import os.path

class MRessGruppeTest(unittest.TestCase) :
    """test MRessGruppe class"""
    def setUp(self):
        self._target = self.get_test_target()
    
    def tearDown(self):
        pass
        
    def get_test_target(self):
        return self.get_test_targets()[0]
    
    def get_test_targets(self):
        testfile = os.path.join(os.path.dirname(__file__), 'testdata/lines_m_ressgruppe.txt')
        items = message_file_reader.read_message_file(testfile)
        return items

    def test_ressgruppe(self):
        self.assertEqual('100', self._target.ressgruppe())

    def test_adressnr(self):
        self.assertEqual('10776', self._target.adressnr())
        
        
    def test_line_with_description(self):
        line = self._target.line_with_description()
        self.assertNotEqual(line, '')           
