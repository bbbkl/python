# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: extract_proc_ids.py
#
# description
"""\n\n
    extract proc ids out of given log file until special process id is reached
"""

import sys
import re

def get_proc_ids(filename, stop_id):
    """read log file, return list with process ids"""
    result = []
    #rgx_proc_id = re.compile(r"begin SolGoalSchedulePrioI::execute scheduling process: p\d+ ([\S]+) ")
    #   1    1 process LA-01315264          dispolevel: 3  pr
    rgx_proc_id = re.compile(r"^\s*\d+\s+\d+\s+process\s+(\S+)\s+dispolevel")
    # rgx_proc_id = re.compile(r"^\s*(\d+)\s+(\d+)\s+process\s+(\S+)\s+dispolevel")
    for line in open(filename):
        # ... begin SolGoalSchedulePrioI::execute scheduling process: p102571 LA-14005165 0 ...
        hit = rgx_proc_id.search(line)
        if hit:
            proc_id = hit.group(1)
            #print proc_id
            if not proc_id in result:
                result.append(proc_id)
            if proc_id == stop_id:
                break
    return result


def get_proc_ids_out_of_xml(xml_filename):
    """get process ids out of xml file"""
    result = []
    rgx_proc_id = re.compile(r'<process id="[^"]+" name="([^"]+)"')
    for line in open(xml_filename):
        # ... begin SolGoalSchedulePrioI::execute scheduling process: p102571 LA-14005165 0 ...
        hit = rgx_proc_id.search(line)
        if hit:
            proc_id = hit.group(1)
            #print proc_id
            if not proc_id in result:
                result.append(proc_id)
    return result

def main():
    """main function"""
    filename = sys.argv[1]
    stop_id  = sys.argv[2]

    process_ids = get_proc_ids(filename, stop_id)
    #process_ids = get_proc_ids_out_of_xml(filename)
    print(",".join(process_ids))
    print(len(process_ids))


if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
