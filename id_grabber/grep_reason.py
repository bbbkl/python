# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: grep_reason.py
#
# description
"""\n\n
    grep reason infos out of given reason xml file
"""

import sys
import re
import os.path
from argparse import ArgumentParser

VERSION = '0.1'

def grep_stat_reasons(filename):
    """parse logfile"""
    result = []
    proc_id = None
    # <TardinessReasonsForActSet actSet="18377004 process='PPA    LA-01194495'">
    rgx_proc_id = re.compile(r"<TardinessReasonsForActSet.*process='[A-Z]{3}\s([^']+)'")
    #<ReasonStructure EarliestEnd="2011-08-08T09:53:00"
    rgx_stat = re.compile(r'ReasonStructure.*EarliestEnd="([^"]+)"')
    # <structureReason typeOfActivitySet="process" idActivitySet="MU-00490461-0050" dueDateActSet="2011-08-04T10:15:00" earliestStartWithCalBreaks="2011-08-04T10:15:00" earliestEndWithCalBreaks="2011-08-04T12:41:00" tardinessWithCalBreaks="P0DT02H26M"/>
    rgx_stat61 = re.compile('<structureReason.*idActivitySet="([^"]+)".*earliestEndWithCalBreaks="([^"]+)"')
    for line in open(filename):
        hit = rgx_proc_id.search(line)
        if hit:
            proc_id = hit.group(1)
            #print(proc_id)
            continue
        
        hit = rgx_stat.search(line)
        if hit:
            val = hit.group(1)
            result.append("%s %s" % (proc_id, val))
            
        hit = rgx_stat61.search(line)
        if hit:
            proc_id, val = hit.group(1), hit.group(2)
            result.append("%s %s" % (proc_id, val))
     
    result.sort()
    return result


def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)

    parser.add_argument('reason_xml', metavar='reason_xml_file', help='reason xml file')

    return parser.parse_args()

def main():
    """main function"""
    args = parse_arguments()
    filename = args.reason_xml

    reasons = grep_stat_reasons(filename)
    for reason in reasons:
        print(reason)

    


if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
