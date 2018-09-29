# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: reorder_activites_csv.py
#
# description
"""\n\n
    for given file with ordered process ids open csv file and reorder with respect to given order
"""

import sys
import re
import os.path

def get_ordered_process_ids(filename_pids):
    """first line contains comma separated list of process ids"""
    pids = open(filename_pids).readline()[:-1].split(',')
    return pids

def get_id_to_line(filename_csv):
    """return mapping: process id -> csv line + 'headline' -> 'csv headline'"""
    line_mapping = {}
    stream = open(filename_csv)
    line_mapping['headline'] = stream.readline()
    for line in stream:
        # 4021;VLA-00641401 CAB 5431991 10 4021;327162;CAB
        #hit = re.search('\d+;([^ ]+)', line)
        hit = re.search('^(\S+|\S+ \S+) (generated|PPA)', line)
        if hit:
            key = hit.group(1)
            line_mapping.setdefault(key, [])
            line_mapping[key].append(line)
    stream.close()
    return line_mapping

def reorder_csvfile(filename_csv, ordered_process_ids):
    """reorder csv file with respect to given process ids"""
    line_mapping = get_id_to_line(filename_csv)
    filename_out = "%s_reordered%s" % os.path.splitext(filename_csv)
    stream = open(filename_out, "w")
    stream.write(line_mapping['headline'])
    for proc_id in ordered_process_ids:
        for line in line_mapping[proc_id]:
            stream.write(line)
    stream.close()

def main():
    """main function"""
    filename_pids = sys.argv[1]
    filename_csv = sys.argv[2]

    process_ids = get_ordered_process_ids(filename_pids)
    reorder_csvfile(filename_csv, process_ids)
    

if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
