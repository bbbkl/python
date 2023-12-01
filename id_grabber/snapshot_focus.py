# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: snapshot_focus.py
#
# description
"""\n\n
    take logfile, sonic.dat, message file and a process <id> of an optimization
    modify message file up to <id> that the start/end time and altres choice of all processes
    before <id> are modified and fixed.
    This enables quick analysis of the critical process <id> without longuish optimization
    before the interesting <id> comes in focus.

TrResource    -10101040-0020S 10848 14312
1    Prozessbereich PPN
2    Prozess        -10101040-0020S
3    Teilprozess    10848
4    AktPos         10
5    ResPos         0
6    ResArt         7 (Arbeitsplatz)
7    Res            30
8    IdentAkt       14312
9    Intensitaet    1
10    alt_group          1
11    BasisRes       1
12    SelectedRes    13101
    OverloadUsed   0

TrActivity    -10101040-0020S 10848 14312 0
1    PBK                     PPN
2    Prozess                 -10101040-0020S
3    Teilprozess             10848
4    AktPos                  10
5    AktArt                  0 (Produktion)
6    IdentAkt                14312
7    Zeitwahl                0
8    Zeit                    0
9    Zeiteinheit             1 (Minuten)
10    TR                      25
11    TE                      4,17
12    ZeitenheitTR            1 (Minuten)
13    ZeiteinheitTE           1 (Minuten)
14    Zeitmengeneinheit       0
15    start_date             17.09.2013
16    end_date               17.09.2013
17    Fixiert                 0
18    BedZeit                 16.09.2013
19    BedArt                  0 (Ohne)
20    Fixtermin               16.09.2013
21    start_time               33600
22    end_time                 43320
23    Unterbrechbar           0
24    #Unterbrechungen        1
25    Zeitraum                0
26    Zeitraum_einheit        1 (Minuten)
27    MinZwischenzeit         0
28    MinZwischenzeit_einheit 1 (Minuten)
29    FertigungsTyp           1
30    Fertig_gemeldet         0
31    cal                100
32    Ruestklasse
33    Partial_lot             0
34    Total_lot_size          25
35    TRTotal                 25
36    TETotal                 104,25
37    Continous_production    0
38    Continous_demand        0
39    PBO                     PPN
"""

import re
import os.path
from argparse import ArgumentParser

VERSION = '0.1'

def add_altres_infos(sonic_file, activity_infos):
    """add altres infos to given activity infos. For each altres info add tuple (res id, res pos) at end"""
    dataline = None
    for line in open(sonic_file):
        if re.search(r'^2\t841', line):  # DEF_APSCommandcreate_MB_Ressource_
            tokens = tokenize(dataline)
            identact = tokens[1]
            res_kind = tokens[2]
            res_id = tokens[3]
            res_pos = tokens[4]
            activity_infos[identact].append((res_kind, res_id, res_pos))
        if re.search(r'^(1\t)?3\t', line):
            dataline = line

def get_activity_infos(sonic_file, encoding_id):
    """return dictionary identact -> (start date, start time, end date, end time, altres choice)"""
    result = {}

    dataline = None
    for line in open(sonic_file, encoding=encoding_id):
        if re.search(r'^(1\t)?2\t840', line) is not None:  # DEF_APSCommandcreate_MB_Aktivitaet
            try:
                tokens = tokenize(dataline)
            except:
                print("line was '%s'" % line)
                raise
            identact = tokens[1]
            startdate = tokens[2]
            starttime = tokens[3]
            enddate = tokens[4]
            endtime = tokens[5]
            partproc = tokens[6]
            proc = tokens[10].strip()  # remove leading/trailing blanks

            if identact == '-1':
                identact = '%s:%s' % (identact, proc)

            result[identact] = [startdate, starttime, enddate, endtime, partproc, proc]
        if re.search(r'^(1\t)?3\t', line):
            dataline = line

    return result

def get_ordered_process_ids(log_file):
    """parse process ordering out of logfile
       return list of process ids sorted by planning order"""
    result = []

    for line in open(log_file):
        hit = re.search(r'process\s+(\S.*\S)\s+dispolevel:\s+\d+\s+priority:', line)
        if hit is None:
            hit = re.search(r'^\s+\d+\s+\d+\s+process=(\S+)', line)
        if hit is None:
            hit = re.search(r'begin SolGoal_scheduleSequenceBlockI::execute scheduling process: (\S.*) id=', line)
        if hit is not None:
            id = hit.group(1)
            if not id in result:
                result.append(hit.group(1))

    return result

def get_process_ids_to_fix(ordered_proc_ids, proc_id, filter_until_proc=True):
    """return set of process ids to fix, either filter until given proc id 
       or return all ids except givent proc id"""
    # filter_until_proc = False
    if filter_until_proc:
        idx = ordered_proc_ids.index(proc_id)
        return set(ordered_proc_ids[:idx])
   
    ids = set(ordered_proc_ids)
    ids.remove(proc_id)
    return ids

def get_activities_to_modify(activity_infos, process_ids):
    """get identact of all activities which belong to a process within process_ids"""
    items = [identact for identact in activity_infos if activity_infos[identact][5] in process_ids]
    return set(items)

def tokenize(dataline):
    """split dataline into tokens"""
    if dataline.find('1\t') == 0:
        dataline = dataline[2:]
    if dataline[-1] == '\n':
        dataline = dataline[:-1]
    return dataline.split('\t')

def join_tokens(tokens):
    """join tokens with delimiter tab and append newline at end"""
    tokens = [str(token) for token in tokens]
    return '\t'.join(tokens) + '\n'

def is_modifiable(activity_tokens):
    """true if activity is not fixed or not done"""
    return activity_tokens[17] == '0'  # and activity_tokens[30] == '0' # 17 - fixed, 30 - done

def to_seconds(time_string):
    """convert time string like 10:58 to seconds"""
    hour, minute = time_string.split(':')
    return int(hour) * 60 * 60 + int(minute) * 60

def modify_activity(dataline, activity_infos, activity_ids, do_fix):
    """if dataline contains id which is in activity_ids, modify data"""
    tokens = tokenize(dataline)
    identact = tokens[6]
    if identact == '-1':
        identact = '%s:%s' % (identact, tokens[2])
    if identact in activity_ids and is_modifiable(tokens):
        startdate, starttime, enddate, endtime = activity_infos[identact][:4]
        tokens[15] = startdate
        tokens[16] = enddate
        tokens[21] = to_seconds(starttime)
        tokens[22] = to_seconds(endtime)
        if do_fix:
            tokens[17] = '1'  # fixed flag
    return join_tokens(tokens)

def modify_resource(dataline, activity_infos, activity_ids):
    """if dataline contains id which is in activity_ids, modify data"""
    tokens = tokenize(dataline)
    identact = tokens[8]
    # if identact in activity_infos: # debug
    if identact in activity_ids:
        altres_infos = activity_infos[identact][6:]
        for altres_info in altres_infos:
            res_id, res_pos = altres_info[1:]  # for res_kind, res_id, res_pos in altres_infos:
            # print("checking %s, %s, %s" % (res_kind, res_id, res_pos))
            if res_pos == tokens[5]:
                tokens[12] = res_id
    return join_tokens(tokens)

def is_dataline_for_command(idx, lines, command):
    """check wheter index points to a dataline at all and dataline belongs to right command"""
    line = lines[idx]
    if len(line) > 0 and not line[0] == '3':
        return False
    # get next relevant command
    pos = idx + 1
    while pos < len(lines):
        line = lines[pos]
        if len(line) > 0:
            if line[0] == '2':
                break
            if line[0] == '3':
                pos = len(lines)
                break
        pos = pos + 1
    if pos < len(lines):
        return re.search(r'^2\t%d' % command, lines[pos]) is not None
    return False
    """
    if len(lines)>idx:
        next_line = lines[idx+1]
        if len(next_line)>0 and next_line[0]=='2':
            return re.search(r'^2\t%d' % command, next_line) is not None
    if len(lines)>idx+1:
        next_line = lines[idx+2]
        if len(next_line)>0 and next_line[0]=='2':
            return re.search(r'^2\t%d' % command, next_line) is not None
    return False
    """

def is_activity_line(idx, lines):
    """true if next following command is 365 = DEF_ERPCommandcreate_Activity_____"""
    return is_dataline_for_command(idx, lines, 365)

def is_resource_line(idx, lines):
    """true if next following command is 350 DEF_ERPCommandcreate_Resource_____"""
    return is_dataline_for_command(idx, lines, 350)

def modify_message_file(message_file, activity_infos, process_ids_to_fix, encoding_id, do_fix=True):
    """change activities/altres selections which belong to process_ids_to_fix, result is <message>.focus.dat"""
    activity_ids = get_activities_to_modify(activity_infos, process_ids_to_fix)

    lines = open(message_file, encoding=encoding_id).readlines()
    for idx in range(len(lines)):
        if is_activity_line(idx, lines):
            lines[idx] = modify_activity(lines[idx], activity_infos, activity_ids, do_fix)
        elif is_resource_line(idx, lines):
            lines[idx] = modify_resource(lines[idx], activity_infos, activity_ids)
    out_file = message_file.replace('.dat', '.focus.dat')
    out = open(out_file, "w", encoding=encoding_id)
    for line in lines:
        out.write(line)
    out.close()

def test_encoding(message_file):
    """check for file encoding"""
    encodings = ["UTF-8", "ISO-8859-1", "latin-1"]
    
    if not os.path.exists(message_file):
        raise FileNotFoundError(message_file)
    
    for item in encodings:
        try:
            for line in open(message_file, encoding=item):
                pass
            return item
        except:
            pass
        
    raise ("Cannot get right encoding, tried %s" % str(encodings))

def parse_arguments():
    """parse arguments from command line"""
    # usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('--sync', action="store_true",  # or store_false
                      dest="synchronization", default=False,  # negative store value
                      help="create synchronization and do not fix activities")
    parser.add_argument('--isolate', action="store_true",  # or store_false
                      dest="isolate", default=False,  # negative store value
                      help="fix activities's of all processes exept given one")
    parser.add_argument('sonic_file', metavar='sonic_file', help='input sonic file')
    parser.add_argument('log_file', metavar='log_file', help='input log file')
    parser.add_argument('process_id', metavar='process_id', help='input process id')
    parser.add_argument('message_file', metavar='message_file', help='input message_file')
    return parser.parse_args()


def main():
    """main function"""
    args = parse_arguments()
    sonic_file = args.sonic_file
    log_file = args.log_file
    proc_id = args.process_id
    message_file = args.message_file

    encoding = test_encoding(args.message_file)

    activity_infos = get_activity_infos(sonic_file, encoding)
    add_altres_infos(sonic_file, activity_infos)

    # for item in activity_infos: print(item, activity_infos[item])
    
    ordered_process_ids = get_ordered_process_ids(log_file)
    
    if args.synchronization:
        modify_message_file(message_file, activity_infos, ordered_process_ids, encoding, False)
        return
    
    process_ids_to_fix = []
    if args.isolate:
        # cnt1 = len(ordered_process_ids)
        process_ids_to_fix = ordered_process_ids
        process_ids_to_fix.remove(proc_id)
        # print("isolate %d -> %d" % (cnt1, len(process_ids_to_fix)))
        # out = open("d:/temp/proc_ids.txt", "w")
        # out.write(str(process_ids_to_fix))
        # out.close()
    else:
        process_ids_to_fix = get_process_ids_to_fix(ordered_process_ids, proc_id)
    # for idx, item in enumerate(process_ids_to_fix): print("%d %s" % (idx, item))
    modify_message_file(message_file, activity_infos, process_ids_to_fix, encoding)

if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
