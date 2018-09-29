# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: reasons_compare.py
#
# description
"""\n\n
    for two given reason xml files (process / part process) compare 
    - processes for which reasons have been found
    - number of reasons for a process
    report differences 
"""

import sys
import re
from argparse import ArgumentParser

VERSION = '0.1'

def get_reasons_partprocess(xml_filename):
    """get partprocess ids out of xml file"""
    result = {}
    # <tardinessReasonCollectionPartProcess idPartProcess="3295005" namePartProcess="PPN    -10101114-0060S / 12662">
    rgx_proc_id = re.compile(r'<tardinessReasonCollectionPartProcess .* namePartProcess="\S+\s+(\S+)')
    for line in open(xml_filename):
        hit = rgx_proc_id.search(line)
        if hit:
            proc_id = hit.group(1)
            result.setdefault(proc_id, 0)
            result[proc_id] += 1
    return result

def get_reasons_process(xml_filename):
    """get process ids out of xml file"""
    result = {}
    #  <tardinessReasonCollectionProcess idProcess="3294004" nameProcess="-10101114-0060S"> 
    rgx_proc_id = re.compile(r'<tardinessReasonCollectionProcess .* nameProcess="([^"]+)"')
    for line in open(xml_filename):
        hit = rgx_proc_id.search(line)
        if hit:
            proc_id = hit.group(1)
            result.setdefault(proc_id, 0)
            result[proc_id] += 1
    return result

def get_reasons_process_details(xml_filename):
    """get process ids out of xml file"""
    result = {}
    #  <tardinessReasonCollectionProcess idProcess="3294004" nameProcess="-10101114-0060S"> 
    rgx_proc_id = re.compile(r'<tardinessReasonCollectionProcess .* nameProcess="([^"]+)"')
    for line in open(xml_filename):
        hit = rgx_proc_id.search(line)
        if hit:
            proc_id = hit.group(1)
            result.setdefault(proc_id, {'cnt', 0})
            result[proc_id]['cnt'] += 1
    return result

def parse_arguments():
    """parse arguments from command line"""
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)

    
    parser.add_argument('xml_process', metavar='reason_xml_process', help='reason xml process')
    parser.add_argument('xml_partprocess', metavar='reason_xml_partprocess', help='reason xml partprocess')
    return parser.parse_args()

def report_diffs( dictIdsProc, dictIdsPartProc ):
    """report differences of ids proc / partproc"""
    for id_proc in dictIdsProc:
        if not id_proc in dictIdsPartProc:
            print("no partproc reason for %s" % id_proc)
        elif dictIdsProc[id_proc] != dictIdsPartProc[id_proc]:
            print("%s proc: %d, partproc: %d" % (id_proc, dictIdsProc[id_proc], dictIdsPartProc[id_proc]))
    for id_proc in dictIdsPartProc:
        if not id_proc in dictIdsProc:
            print("no proc reason for %s" % id_proc)

def main():
    """main function"""
    args = parse_arguments()
    
    idsProc = get_reasons_process(args.xml_process)
    idsPartProc = get_reasons_partprocess(args.xml_partprocess)
    
    report_diffs( idsProc, idsPartProc)


if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
