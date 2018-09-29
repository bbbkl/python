# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: ctp_performance.py
#
# description
"""\n\n
   grep abs msecs, ctp no, msecs this ctp out of given logfile
"""

import sys
import re

def grep_data(filename):
    """open file, grep data, write to stdout"""
    rgx = re.compile(r'abs_msecs\: (\d+) trace.*end calcCtp Nr=(\d+).*elapsed msecs: (\d+)')
    for line in open(filename):
        hit = rgx.search(line)
        if hit:
            msecs_absolute, ctp_no, msecs_ctp = hit.groups()
            print("%s;%s;%s" % (ctp_no, msecs_ctp, msecs_absolute)) 

def main():
    """main function"""
    filename = sys.argv[1]

    grep_data(filename)

if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
