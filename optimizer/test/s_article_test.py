# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: article_test.py
#
# description
"""\n\n
    Test Article class
"""

import unittest
import message_file_reader
import os.path

class ML_ArtOrtTest(unittest.TestCase) :
    """test Article class"""
    def setUp(self):
        # 3    0013838  <tab>    0    0    0    0
        self._target = self.get_test_target()
    
    def tearDown(self):
        pass
        
    def get_test_target(self):
        testfile = os.path.join(os.path.dirname(__file__), 'testdata/lines_s_article.txt')
        items = message_file_reader.read_message_file(testfile)
        return items[0]

    def test_article_id(self):
        self.assertEqual('0013838', self._target.article_id())
        
    def test_chargenart(self):
        self.assertEqual('', self._target.chargenart())
    
    def test_art_var_typ(self):
        self.assertEqual('0', self._target.art_var_typ())
    
    def test_kommissionslager(self):
        self.assertEqual('0', self._target.kommissionslager())
    
    def test_wbz(self):
        self.assertEqual(0, self._target.wbz())
    
    def test_wbz_overload(self):
        self.assertEqual(0, self._target.wbz_overload())
      
    def test_floatingpoint_multiplier(self):
        self.assertEqual(100, self._target.floatingpoint_multiplier())    
              
    def test_line_with_description(self):
        line = self._target.line_with_description()
        self.assertNotEqual(line, '')