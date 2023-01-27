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

    def get_id(self):
        if self._id.find('Proxy'):
            return get_demand_proxy_short_name(self._id)
        return self._id

    def __str__(self):
        diff = minutes_2_timestr(self.get_diff())
        multiflag = '*' if self.get_multi_diff() < self.get_nonmulti_diff() else ' '
        msg = "%-30s diff=%s%s   delay=%-13s %s" % (self.get_id(), diff, multiflag, self.delay, str(self.time_late))
        return msg

    def __cmp__(self, other):
        return self.get_diff() < other.get_diff()

    def add_delay(self, delay):
        self.delay = reformat_timestring(delay)
    def add_timelate(self, time_late):
        self.time_late.append(time_late)
    def no_reason(self):
        return len(self.time_late) == 0

    def has_multi_reason(self):
        multi_items = [x for x in self.time_late if x[-3:] in ('mmr', 'mrr')]
        return len(multi_items) > 0

    def get_multi_diff(self):
        multi_items = [x for x in self.time_late if x[-3:] in ('mmr', 'mrr')]
        multi_delay = max(timestr_2_minutes(x) for x in multi_items) if multi_items else 0
        return timestr_2_minutes(self.delay) - multi_delay

    def get_nonmulti_diff(self):
        stc_items = [x for x in self.time_late if x[-3:] == 'stc']
        tbd_items = [x for x in self.time_late if x[-3:] in ('tbd', 'pre')]
        # multi_items = [x for x in self.time_late if x[-3:] in ('mmr', 'mrr')]
        other_items = [x for x in self.time_late if x[-3:] not in ('stc', 'tbd', 'pre', 'mmr', 'mrr')]
        stc_delay = max(timestr_2_minutes(x) for x in stc_items) if stc_items else 0
        tbd_delay = max(timestr_2_minutes(x) for x in tbd_items) if tbd_items else 0
        baseline_delay = stc_delay + tbd_delay
        other_delay = max(timestr_2_minutes(x) for x in other_items) if other_items else 0
        return timestr_2_minutes(self.delay) - baseline_delay - other_delay

    def get_diff(self):
        return min(self.get_nonmulti_diff(), self.get_multi_diff())

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
                  'timeBound' : 'tbd', 'resource' : 'res', 'material' : 'mat', 'precedence' : 'pre',
                  'multi_resources' : 'mrr', 'multi_mat_resources' : 'mmr'}
    hit = re.search(r'reason=(combi_matres|material|combi_resres|resource|structure|timeBound|precedence|multi_resources|multi_mat_resources)', line)
    if hit:
        return '_%s' % short_name[hit.group(1)]
    return '_NNN'

def get_demand_proxy_short_name(long_version):
    if long_version.find('SafetyStock') != -1:
        mat = re.search(r'\|([^\|]*)', long_version).group(1)
        return 'Proxy_SS/%s' % mat
    if long_version.find('DemandProxy_fixed_mat') != -1:
        mat = re.search(r'\|([^\|]*)', long_version).group(1)
        pfx = long_version[:long_version.find('/')]
        pfx = pfx.replace(' PPA', '').replace(' ', '/')
        return "Proxy_FX/%s/%s" % (pfx, mat)
    return long_version

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
            """
            use_multi = 1
            is_multi = line.find('multi')!=-1
            if use_multi and not is_multi:
                continue
            if not use_multi and is_multi:
                continue
            """
            new_reason.add_timelate(hit.group(1) + get_reason_type(line))
    if new_reason is not None:
        reasons.append(new_reason)
    return reasons


def report_no_reasons(reasons, stream):
    items = []
    for item in reasons:
        if item.get_diff != 0 and item.no_reason():
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
        if not zero_diff and item.get_diff == 0:
            zero_diff = True
            stream.write(100 * '-' + '\n')
        elif zero_diff and item.get_diff != 0:
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
