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

from command_mapper import CommandMapper

NUM2TEXT_DICT = None
def get_erp_commands():
    """get mapping code -> readable ERP command"""
    global NUM2TEXT_DICT
    if NUM2TEXT_DICT is None:
        NUM2TEXT_DICT = parse_erp_commands()
    return NUM2TEXT_DICT

def parse_erp_commands():
    """parse ERP commands file"""
    filename = CommandMapper.get_apsERPCommands_file()
    num2text = {}
    for line in open(filename):
        hit = re.search("#define\s+(\S+)\s+(\d{3})", line)
        if hit:
            text, num = hit.groups()
            num2text[num] = text
    return num2text

def describe_command(line):
    """for command '2 <nnn>' add human readable command description to line"""
    hit = re.search("^2\t(\d{3})$", line)
    if hit:
        num2text = get_erp_commands()
        text = num2text[hit.group(1)]
        line = "%s\t%s\n" % (line[:-1], text)
    return line

def replace_codes(command_file, encoding_id):
    """for each command '2 <nnn>' add human readable command to line"""
    result_file = command_file[:-4] + "_readable" + command_file[-4:]
    out = open(result_file, 'w', encoding=encoding_id)
    for line in open(command_file, encoding=encoding_id):
            out.write(describe_command(line))
    out.close()


def main():
    """show hello python message"""
    dat_file = sys.argv[1]
    replace_codes(dat_file) 
    return 0

if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
