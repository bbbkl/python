# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: diff_procs_of_resultfile.py
#
# description
"""\n\n
    take two result files, extract proc ids, report proc ids with different lines within result files
"""

import sys
import re

def diff_activities(filename1, filename2):
    proc_ids = set()
    with open(filename1) as file1, open(filename2) as file2:
        for line1, line2 in zip(file1, file2):
            if line1 != line2:
                hit = re.search(r"^(\S+)", line1)
                if hit:
                    proc_ids.add(hit.group(1))
    return proc_ids


def get_proc_to_line(filename):
    """read result file, return dict: proc_id -> line"""
    result = {}
    rgx_proc_id = re.compile(r"^[A-Z]+(?:/|\s+)([^;]+);")
    ordered_ids = []
    for line in open(filename):
        # """PPA    AP-04076522-0030;2011-07-29 00:00:00;2011-07-27 07:34:00;2011-08-02 06:40:00;885465"""
        hit = rgx_proc_id.search(line)
        if hit:
            proc_id = hit.group(1)
            if not proc_id in ordered_ids:
                ordered_ids.append(proc_id)
            #print proc_id
            result[proc_id] = line
    return result, ordered_ids

def get_proc_ids_which_differ(filename1, filename2):
    """get proc ids which exist in both files but have different content line"""
    if filename1.find("activities") != -1:
        return diff_activities(filename1, filename2)
    result = []
    dict1, ordered_ids1 = get_proc_to_line(filename1)
    dict2               = get_proc_to_line(filename2)[0]
    for proc_id in ordered_ids1:
        if proc_id in dict2 and dict1[proc_id] != dict2[proc_id]:
            result.append(proc_id)
    return result

def main():
    """main function"""
    result_file1 = sys.argv[1]
    result_file2 = sys.argv[2]

    process_ids = get_proc_ids_which_differ(result_file1, result_file2)
    print(",".join(process_ids))


if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
