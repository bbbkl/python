# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: CommandMapper_test.py
#
# description
"""\n\n
    Test command mapping
"""

import unittest
from command_mapper import CommandMapper

class CommandMappperTest(unittest.TestCase) :
    """test Article class"""
    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    def test_num2text(self):
        mapping = CommandMapper.num2text()
        result = mapping[335]
        self.assertEqual('DEF_ERPCommandcreate_MD_Artikel___', result)
        
    def test_text2num(self):
        mapping = CommandMapper.text2num()
        result = mapping['DEF_ERPCommandcreate_MD_Artikel___']
        self.assertEqual(335, result)
