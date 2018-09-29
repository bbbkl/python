# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: zimmer.py
#
# description
"""\n\n
    check integrity of optimizer data for listener (sonic data)
"""

import sys
import re

def check_datfile(dat_file):
    hit_count = 0
    line_count = 0
    dataline = None
    rgxCmd = re.compile(r'^2\t842')
    for line in open(dat_file):
        line_count += 1
        if rgxCmd.search(line):
            hit_count += 1
            if dataline is None:
                print("no data for command in line %d" % line_count)
            elif dataline[0] != '3' or dataline.count('\t') != 5:
                print("strange data for command in line %d" % line_count)
            dataline = None
        else:
            dataline = line
    print("hit_count=%d" % hit_count)
            
def main():
    """main function"""
    dat_file = sys.argv[1]
   
    check_datfile(dat_file)

if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
