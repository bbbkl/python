# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: check_selected_altres.py
#
# description
"""\n\n
    report altres and their selections
"""

import sys
import re
from argparse import ArgumentParser

VERSION = '0.1'

class SchedulingTrigger:
    """parsed scheduling trigger"""
    def __init__(self, tokens, line_idx):
        self._tokens = tokens
        self._demand_id = tokens[1]
        self._cover_id = tokens[4]

    def key(self):
        #return "%s" % self._tokens[1]
        return "%s/%s" % (self._tokens[1], self._tokens[4])

    def __lt__(self, other):
        return self.key() < other.key()

    def __str__(self):
        return "demandObjType=%s (%s) " % (self._tokens[0], scheduling_obj_type(self._tokens[0])) + \
            "demandId=%s " % self._tokens[1] + \
            "demand_date=%s " % self._tokens[2] + \
            "coverObjType=%s (%s) " % (self._tokens[3], scheduling_obj_type(self._tokens[3])) + \
            "coverId=%s " % self._tokens[4][:-1]


class SchedulingInfo:
    """parsed scheduling info"""
    def __init__(self, tokens, line_idx):
        self._tokens = tokens
        self._obj_type_code = int(tokens[0])
        self._obj_id = tokens[1]
        self._mrp_level = int(tokens[4])
        self._pos = int(tokens[6])
        self._age = int(tokens[7])
        self._line_idx = line_idx

    def key(self):
        return "%s" % self._tokens[1]
        #return "%s/%s" % (self._tokens[0], self._tokens[1])

    def __lt__(self, other):
        return self.key() < other.key()

    def __str__(self):
        return "objTypeCode=%d (%s) " % (self._obj_type_code, scheduling_obj_type(self._obj_type_code)) + \
            "objId=%s " % self._obj_id + \
            "prio=%s " % self._tokens[2] + \
            "date=%s " % self._tokens[3] + \
            "mrpLevel=%s " % self._mrp_level + \
            "ovl=%s " % self._tokens[5] + \
            "pos=%d " % self._pos + \
            "age=%d " % self._age

def to_int(val):
    """turn given string value into a number, -1 for an empty string"""
    if val != '':
        return int(val)
    return -1

def scheduling_obj_type(val):
    """Scheduling type
       Undefined = -1,
       MRPMovementDemand = 0,
       FixedActivityDemand = 1,
       Activity = 2,
       TempActivity = 3,
       PartProc = 4,
       TempPartProc = 5,
       ActivityFallback = 6, // Number used in ERP
       TempActivityFallback = 7 // Number used in ERP
    """
    val = to_int(val)
    if val == 0: return 'MRPMovementDemand'
    if val == 1: return 'FixedActivityDemand'
    if val == 2: return 'Activity'
    if val == 3: return 'TempActivity'
    if val == 4: return 'PartProc'
    if val == 5: return 'TempPartProc'
    if val == 6: return 'ActivityFallback'
    if val == 7: return 'TempActivityFallback'
    return 'undefined'

def parse_items( messagefile ):
    """count contained commands"""
    idx = 0
    rgx_info = re.compile(r'^2\t824') # 824    DEF_APSCommandcreate_SchedInfo____
    rgx_trigger = re.compile(r'^2\t825') # 825    DEF_APSCommandcreate_SchedTrigger_
    prev_line = ''
    infos = []
    triggers = []
    for line in open(messagefile):
        idx += 1

        if rgx_info.search(line):
            tokens = prev_line.split('\t')
            infos.append(SchedulingInfo(tokens[1:], idx))

        if rgx_trigger.search(line):
            tokens = prev_line.split('\t')
            triggers.append(SchedulingTrigger(tokens[1:], idx))

        if len(line) > 0 and line[0] == "3":
            prev_line = line
    return infos, triggers

def pretty_print(items, show_all):
    """pretty print dict to console"""
    key_prev = ""
    for item in sorted(items):
        if key_prev!="" and key_prev == item.key():
            print(item)
        if show_all:
            print(item)
        key_prev = item.key()

def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('message_file', metavar='message_file', help='input message file')
    parser.add_argument('-a', '--show_all', action="store_true", # or stare_false
                      dest="show_all", default=False, # negative store value
                      help="show all parsed sched info/trigger items on console")
    return parser.parse_args()

def main():
    """main function"""
    args = parse_arguments()
    sched_infos, sched_triggers = parse_items(args.message_file)
    sched_infos.sort()
    sched_triggers.sort()

    print("### scheduling_infos #=%d ###" % len(sched_infos))
    pretty_print(sched_infos, args.show_all)
    print("### scheduling_triggers #=%d ###" % len(sched_triggers))
    pretty_print(sched_triggers, args.show_all)

if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
