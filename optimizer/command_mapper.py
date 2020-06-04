# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: datfileParser.py
#
# description
"""\n\n
    parse dat file
"""
#

import re
import sys
import os.path

class CommandMapper:
    """map command id to readable define and vice versa"""
    num2text_dict = None
    text2num_dict = None

    def __init__(self):
        """constructor"""
        pass

    @classmethod
    def get_script_path(cls):
        return os.path.dirname(os.path.realpath(sys.argv[0]))

    @classmethod
    def num2text(cls):
        if cls.num2text_dict is None:
            num2text_dict = cls.parse_erp_commands()
        return num2text_dict

    @classmethod
    def text2num(cls):
        if cls.text2num_dict is None:
            cls.text2num_dict = {}
            src = cls.num2text()
            for key in src:
                cls.text2num_dict[src[key]] = key
        return cls.text2num_dict

    @classmethod
    def get_apsERPCommands_file(cls):
        """get absolute path to apsERPCommands.h file"""
        return os.path.join(cls.get_script_path(), "apsERPCommands.h")

    @classmethod
    def parse_erp_commands(cls):
        """parse ERP commands file"""
        filename = cls.get_apsERPCommands_file()
        num2text = {}
        for line in open(filename):
            hit = re.search(r"#define\s+(\S+)\s+(\d{3}\S*)", line)
            if hit:
                text, num = hit.groups()
                num2text[int(num)] = text
        return num2text

