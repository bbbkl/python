# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: id_grabber.py
#
# description
"""\n\n
    take collector export as input and grep related process ids for given id of type xxx
"""

import sys
import re
import os.path
from argparse import ArgumentParser

VERSION = '0.1'

def parse_line(line, pattern):
    """parse one single line"""
    hit = re.search(pattern, line)
    if not hit:
        return None
    return line

def parse_logfile(filename, pattern):
    """parse logfile"""
    result = []
    for line in open(filename):
        if line.find("=== Process statistics ====") != -1: # only consider first otpimization
            break
        item = parse_line(line, pattern)
        if item:
            result.append(item)
    return result

def grep_activity_ids_for_res_id(filename, resource_id):
    """for given resource id, get related activity ids"""
    activity_ids = []
    rgx = re.compile("(?:disResReq|(?:altR|r)esourceCst) activityID=\"([^\"]+)\".*(?:altResSetID|resourceID)=\"%s\"" % resource_id)
    for line in open(filename):
        hit = rgx.search(line)
        if hit:
            #print("activity: %s" % hit.group(1))
            activity_id = hit.group(1)
            if not activity_id in activity_ids:
                activity_ids.append(activity_id)
    return activity_ids

def grep_proc_id_for_activity_id(filename, activity_id):
    """get proc id for given activity id"""
    # <activity id="a4291" name="LA-02285817 PPA 283481
    map_activity_to_process = get_map_activity_to_process(filename)
    if activity_id in map_activity_to_process:
        return map_activity_to_process[activity_id]
    return None

MAP_ACTIVITY_TO_PROCESS = None
def get_map_activity_to_process(filename):
    """get global mapping activity id to process name"""
    global MAP_ACTIVITY_TO_PROCESS
    # <activity id="a4291" name="LA-02285817 PPA 283481
    if MAP_ACTIVITY_TO_PROCESS is None:
        MAP_ACTIVITY_TO_PROCESS = {}
        rgx = re.compile("<activity id=\"([^\"]+)\" name=\"([^ ]+) ")
        for line in open(filename):
            hit = rgx.search(line)
            if hit:
                MAP_ACTIVITY_TO_PROCESS[hit.group(1)] = hit.group(2)
    return MAP_ACTIVITY_TO_PROCESS

def grep_proc_ids_for_resource_id(filename, resource_id):
    """get proc ids which use given resource id"""
    activity_ids = grep_activity_ids_for_res_id(filename, resource_id)

    process_ids = []
    for activity_id in activity_ids:
        process_id = grep_proc_id_for_activity_id(filename, activity_id)
        if process_id is not None and not process_id in process_ids:
            #print process_id
            process_ids.append(process_id)

    return process_ids

def get_proc_id_of_process_line(process_data):
    """get process id for given process data lien"""
    tokens = process_data.split('\t')
    return tokens[2]

def get_proc_id_of_material_line(material_data):
    """get process id for given material data line"""
    tokens = material_data.split('\t')
    return tokens[2]

def grep_proc_ids_for_material_id(filename, material_id):
    """get proc ids which use given resource id"""
    process_ids = []
    rgx_process = re.compile(r'^2\t370')
    rgx_material = re.compile(r'2\t355')
    hit_process = hit_material = None
    for line in open(filename):
        if hit_process or hit_material:
            if line.find(material_id) != -1:
                if hit_process:
                    process_ids.append(get_proc_id_of_process_line(line))
                if hit_material:
                    process_ids.append(get_proc_id_of_material_line(line))
        elif rgx_process.search(line):
            hit_process = True
            continue
        elif rgx_material.search(line):
            hit_material = True
            continue
        hit_process = hit_material = None
    
    return process_ids

def grep_proc_begin_end(filename, process_id):
    """go through file and ignore all lines up to
       begin SolGoalSchedulePrioI::execute scheduling process
       until next occurence of
       end/fail SolGoalSchedulePrioI::execute scheduling process
       write lines to dir/process.log
    """
    rgx_on = re.compile("begin SolGoalSchedulePrioI::execute scheduling process.*%s" % process_id)
    rgx_off = re.compile("(end|fail) SolGoalSchedulePrioI::execute scheduling process.*%s" % process_id)
    output_file = os.path.join(os.path.dirname(filename), "%s.log" % process_id)
    output = open(output_file, "w")
    output_mode = False

    for line in open(filename):
        if output_mode == False and rgx_on.search(line):
            output_mode = True

        if output_mode == True:
            output.write(line)
            if rgx_off.search(line):
                output_mode = False
                output.write("\n\n\n")

def grep_proc_ids_subproc_own_duedate(messagefile):
    """open file and grep for non-head partprocs with own due date.
       return ids of processes.
    """
    proc_ids = set()
    rgx_process = re.compile("^2\t370")
    dataline = ''
    for line in open(messagefile):
        if rgx_process.search(line) and dataline != '':
            tokens = dataline.split('\t')
            is_head = tokens[17] == '1'
            use_duedate = tokens[23] == '1'
            if not is_head and use_duedate:
                proc_id = tokens[2]
                proc_ids.add(proc_id)
            dataline = ''
        else:
            dataline = line
    return proc_ids 

def grep_ordered_proc_ids(logfile):
    """for given logfile get ordered process ids"""
    # 5.2 line:   46  158 process LA-01194016          dispolevel:  1 
    # 6.1 line: begin SolGoalSchedulePrioI::execute scheduling process: p98738 LA-00016297
    proc_ids = []
    rgx1 = re.compile(r"^\s*\d+\s+\d+\s+process\s+(\S+)\s+dispolevel")
    rgx2 = re.compile(r"begin SolGoalSchedulePrioI::execute scheduling process: p\d+\s+([\-A-Z]\S+)")
    rgx3 = re.compile(r"begin SolGoalSchedulePrioI::execute scheduling process: p\d+\s+\d+\s+([\-A-Z]\S+)")
    rgx4 = re.compile(r"begin SolGoal_scheduleSequenceBlockI::execute scheduling process: (\S.*) id=")
    for line in open(logfile):
        hit = rgx1.search(line) or rgx2.search(line) or rgx3.search(line) or rgx4.search(line)
        if hit:
            proc_id = hit.group(1)
            if not proc_id in proc_ids:
                proc_ids.append(proc_id)
    return proc_ids

def grep_proc_ids_before_timepoint(filename, timepoint):
    """expected input is a headporc result csv file. Grep all proc ids with end time < timepoint"""
    ids = []
    for line in open(filename):
        if line.count(';') > 1:
            tokens = line.split(';')
            if tokens[-2] < timepoint:
                proc_id = tokens[0][4:]
                ids.append(proc_id)
    return ids


def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)

    parser.add_argument('input_file', metavar='input_file', help='input file (default log file)')
    parser.add_argument('-rid', '--res_id', metavar='string',
                      dest="res_id", default='',
                      help="grep process ids of processes which require given resource id, input collector export")
    parser.add_argument('-mid', '--mat_id', metavar='string',
                      dest="mat_id", default='',
                      help="grep process ids of processes which consume or produce material id, input message file")
    parser.add_argument('--partproc_duedate', action="store_true", # or store false)
                        dest='partproc_duedate', default=False, 
                        help="grep ids of processes which contain a partproc with own duedate, input message file")

    parser.add_argument('--end_before_timepoint', metavar='string',
                        dest='end_before_timepoint', default='', 
                        help="grep ids of processes which end before given timepoint e.g. '2018-11-15 14:10:00', input headproc result csv file")
    return parser.parse_args()

def main():
    """main function"""
    args = parse_arguments()
    filename = args.input_file

    if args.res_id != '':
        process_ids = grep_proc_ids_for_resource_id(filename, args.res_id)
        print(','.join(process_ids))
        return 0
    
    if args.mat_id != '':
        process_ids = grep_proc_ids_for_material_id(filename, args.mat_id)
        print(','.join(process_ids))
        return 0
    
    if args.partproc_duedate:
        process_ids = grep_proc_ids_subproc_own_duedate(filename)
        print(','.join(process_ids))
        return 0
    
    if args.end_before_timepoint:
        process_ids = grep_proc_ids_before_timepoint(filename, args.end_before_timepoint)
        print(','.join(process_ids))
        return 0
    
    process_ids = grep_ordered_proc_ids(filename)
    
    print(','.join(process_ids))
    #print('#proc_ids=%d' % len(process_ids))

    #grep_proc_begin_end(filename, resource_id)


if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
