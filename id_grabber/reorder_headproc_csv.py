# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: reorder_headproc_csv.py
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
        # PPA    AB-3246;2013-05-03 00:00:00;2013-05-02 23:58:00;2013-05-03 00:00:00
        hit = re.search('\S+\s+([^;]+)', line)
        if hit:
            # remove ';' at end of line to make 6.1 comparable to 5.2 
            if line [-2] == ';':
                line = line [:-2] + "\n"
            line_mapping[hit.group(1)] = line
    stream.close()
    return line_mapping

def reorder_csvfile(filename_csv, ordered_process_ids):
    """reorder csv file with respect to given process ids"""
    line_mapping = get_id_to_line(filename_csv)
    filename_out = "%s_reordered%s" % os.path.splitext(filename_csv)
    stream = open(filename_out, "w")
    stream.write(line_mapping['headline'])
    for proc_id in ordered_process_ids:
        stream.write(line_mapping[proc_id])
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
