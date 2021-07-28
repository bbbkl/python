# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: reasons_timediff.py
#
# description
"""\n\n
    for two given reason text file compare
        delay of part process to
        time_late info of reasons
"""

import re
import sys
import os
from argparse import ArgumentParser

VERSION = '0.1'

class ReasonItem:
    """one reason item"""
    def __init__(self, proc_id):
        self._id = proc_id
        self.delay = -1
        self.time_late = []

    def __str__(self):
        diff = minutes_2_timestr(self.get_diff())
        #diff = self.get_diff()
        msg = "%-30s diff=%s   delay=%-13s %s" % (self._id, diff, self.delay, str(self.time_late))
        return msg

    def __cmp__(self, other):
        return self.get_diff() < other.get_diff()

    def add_delay(self, delay):
        self.delay = reformat_timestring(delay)
    def add_timelate(self, time_late):
        self.time_late.append(time_late)
    def no_reason(self):
        return len(self.time_late) == 0

    def get_diff(self):
        baseline_items = [x for x in self.time_late if x[-3:] == 'stc']
        other_items = [x for x in self.time_late if x[-3:] != 'stc']
        # if we have no structure reason, take timebound as baseline
        timebound_ids = ['tbd', 'pre']
        if len(baseline_items) == 0:
            baseline_items = [x for x in self.time_late if x[-3:] in timebound_ids]
            other_items = [x for x in self.time_late if x[-3:] not in timebound_ids]
        baseline_delay = max(timestr_2_minutes(x) for x in baseline_items) if baseline_items else 0
        other_delay = max(timestr_2_minutes(x) for x in other_items) if other_items else 0
        return timestr_2_minutes(self.delay) - baseline_delay - other_delay

def reformat_timestring(timestring):
    minutes = timestr_2_minutes(timestring)
    return minutes_2_timestr(minutes)

def timestr_2_minutes(timestring):
    """P8DT00H00M -> 8 * 24 * 60"""
    hit = re.search(r'P(\d+)DT(\d+)H(\d+)M', timestring)
    days, hours, minutes = hit.groups()
    return int(days) * 24 * 60 + int(hours) * 60 + int(minutes)

def minutes_2_timestr(minutes_total):
    ticks = abs(minutes_total)
    days = ticks // (24 * 60)
    hours = (ticks - days * 24 * 60) // 60
    minutes = ticks % 60
    if minutes_total < 0:
        return "-P%02dDT%02dH%02dM" % (days, hours, minutes)
    return "P%02dDT%02dH%02dM" % (days, hours, minutes)

def get_reason_type(line):
    short_name = {'combi_matres' : 'cmr', 'combi_resres' : 'crr', 'structure' : 'stc',
                  'timeBound' : 'tbd', 'resource' : 'res', 'material' : 'mat', 'precedence' : 'pre'}
    hit = re.search(r'reason=(combi_matres|material|combi_resres|resource|structure|timeBound|precedence)', line)
    if hit:
        return '_%s' % short_name[hit.group(1)]
    return '_NNN'


def get_reasons(reason_file):
    reasons = []
    rgx_start = re.compile(r'^(?:Cluster|PartProcess)=(.*)$')
    rgx_delay = re.compile(r'\sdelay=(\S+)')
    rgx_timelate = re.compile(r'timeLate=(\S+)')
    new_reason = None
    for line in open(reason_file):
        hit = rgx_start.search(line)
        if hit:
            if new_reason is not None:
                reasons.append(new_reason)
            new_reason = ReasonItem(hit.group(1))
            continue
        if new_reason is None:
            continue
        hit = rgx_delay.search(line)
        if hit:
            new_reason.add_delay(hit.group(1))
            continue
        hit = rgx_timelate.search(line)
        if hit:
            new_reason.add_timelate(hit.group(1) + get_reason_type(line))
    return reasons


def report_no_reasons(reasons, stream):
    items = []
    for item in reasons:
        if item.get_diff() != 0 and item.no_reason():
            items.append(item)
    pct = 100.0 * len(items) / (max(1.0, len(reasons)))
    stream.write("#delayed_with_no_reason=%d (%0.1f%%) out of total %d\n"
                 % (len(items), pct, len(reasons)))
    for item in items:
        stream.write("%s\n" % item)
    stream.write("\n\n")


def report_diffs(reasons, stream):
    zero_diff = False
    for item in reasons:
        if not zero_diff and item.get_diff() == 0:
            zero_diff = True
            stream.write(100 * '-' + '\n')
        elif zero_diff and item.get_diff() != 0:
            zero_diff = False
            stream.write(100 * '-' + '\n')
        stream.write("%s\n" % item)

def process_file(reason_file, with_no_reasons, stream):
    reasons = get_reasons(reason_file)
    reasons = sorted(reasons, key=lambda x: x.get_diff())

    if with_no_reasons:
        report_no_reasons(reasons, stream)

    report_diffs(reasons, stream)

def parse_arguments():
    """parse arguments from command line"""
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('reason_file', metavar='reason_file', help='reason text file')
    parser.add_argument('-n', '--report_delayed_with_no_reasons', action="store_true", # or stare_false
                        dest="report_no_reasons", default=False, # negative store value
                        help="show delayed with no reasons")
    parser.add_argument('-b', '--batch_run', action="store_true", # or stare_false
                        dest="batch_run", default=False, # negative store value
                        help="treat reason_file as start dir and process all reason.txt files")

    return parser.parse_args()


def main():
    """main function"""
    args = parse_arguments()

    if args.batch_run:
        start_dir = args.reason_file
        for root, _, files in os.walk(start_dir):
            for item in list(filter(lambda x: x.find('reasons.txt') != -1 and x.find('_ctp') == -1, files)):
                reason_file = os.path.join(root, item)
                dst = os.path.join(root, item.replace('reasons.txt', 'reasons.diff.txt'))
                print(dst)
                process_file(reason_file, args.report_no_reasons, open(dst, 'w'))
    else:
        process_file(args.reason_file, args.report_no_reasons, sys.stdout)

if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
