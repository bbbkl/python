# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: handle_testmessage.py
#
# description
"""\n\n
    parse testrunner output and report handled testmessages with 1=success, 0=fail
"""

import sys
import re

def parse_testmessages(filename):
    """read log file, return list with process ids"""
    result = {}
    rgx_testmessage = re.compile(r"handle message file (\S.*\.dat)")
    rgx_error = re.compile(r"error\: Value of\: result")
    current_id = None
    for line in open(filename):
        # ... begin SolGoalSchedulePrioI::execute scheduling process: p102571 LA-14005165 0 ...
        hit = rgx_testmessage.search(line)
        if hit:
            current_id = hit.group(1)
            result[current_id] = 1
            continue
        hit = rgx_error.search(line)
        if hit:
            if current_id is not None:
                result[current_id] = 0
            current_id = None
    return result

def report(testmessage_info):
    """pretty print testmessage -> 1/0 to console"""
    for key, value in sorted(testmessage_info.items()):
        print("%s;%d" % (key, value))

def main():
    """main function"""
    filename = sys.argv[1]
    
    testmessage_info = parse_testmessages(filename)
    report(testmessage_info)

if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
