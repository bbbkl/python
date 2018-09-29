# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: process_info_csv.py
#
# description
"""\n\n
    for given headproc.csv file and a logfile of an optimizer run. Extract dispolevel and priority for each process id.
    Write results to console.
"""

import sys
import re

def get_proc_ids_csvfile(csv_file):
    """get list of all process ids out of given csv file"""
    result = []
    rgx_proc_id = re.compile(r'^([^\t]*)\t([^;]*);([^;]+);')
    for line in open(csv_file):
        # ... begin SolGoalSchedulePrioI::execute scheduling process: p102571 LA-14005165 0 ...
        hit = rgx_proc_id.search(line)
        if hit:
            pbk = hit.group(1)
            pid = hit.group(2)
            due_date = hit.group(3)
            result.append((pbk, pid, due_date))
    return result

def get_process_info_logfile(log_file):
    """rely on ordered output of processes, sample '   4    4 process LA-13709277          dispolevel:  1 priority: 1.000000 duedate: -52095 *fixed*'
       return a dictionary pid -> tuple (planning pos, dispolevel, prio, is_fixed)
    """
    result = {}
    rgx_proc = re.compile(r'^\s*(\d+)\s+(\d+)\s+process\s+(\S+)\s+dispolevel\:\s+(\d+)\s+priority\:\s([0-9\.]+)\s+')
    for line in open(log_file):
        hit = rgx_proc.search(line)
        if hit:
            pos_without_fixed = int(hit.group(1))
            pos_with_fixed = int(hit.group(2))
            pid = hit.group(3)
            dpl = int(hit.group(4))
            prio = hit.group(5)
            is_fixed = 1 if line.find('*fixed*') != -1 else 0
            is_done = 1 if line.find('*done*') != -1 else 0
            result[pid] = (pos_without_fixed, pos_with_fixed, dpl, prio, is_fixed, is_done)
    return result

def process_info_csv(csv_file, log_file):
    """get information out of given csv/log file and write process info back to console"""
    process_tuples = get_proc_ids_csvfile(csv_file)
    process_infos = get_process_info_logfile(log_file)

    if len(process_tuples) != len(process_infos):
        raise Exception('inconsistent length of process tuples (csv) and process infos (log)')

    print('Name_Process;Pos_with_fixed;Dispolevel;Prio;fixed;done;WT')
    for pbk, pid, due_date in process_tuples:
        pos_with_fixed, dpl, prio, is_fixed, is_done = process_infos[pid][1:]
        prio = prio.replace('.', ',')
        print('%s\t%s;%d;%d;%s;%d;%d;%s' % (pbk, pid, pos_with_fixed, dpl, prio, is_fixed, is_done, due_date))

def main():
    """main function"""
    csv_file = sys.argv[1]
    log_file = sys.argv[2]

    process_info_csv(csv_file, log_file)

if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
