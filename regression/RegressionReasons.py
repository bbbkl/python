# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: RegressionReasons.py
#
# description
"""\n\n
    regression reason text file pair reference/result
"""

from argparse import ArgumentParser
import filecmp
from enum import IntEnum
import re
from RegressionResultCodes import Regr
import RegressionUtil

VERSION = '1.0'

class ReasonType(IntEnum):
    """reason type"""
    PARTPROC = 0
    CLUSTER = 1
    CLUSTER_HEAD = 2
    UNKNOWN = 3

    def __str__(self):
        if self == 0:
            return "PARTPROC"
        if self==1:
            return "CLUSTER"
        if self==2:
            return "CLUSTER-HEAD"
        return "UNKNOWN"

def to_reason_type(val):
    """string to reason type"""
    if val=="PartProcess":
        return ReasonType.PARTPROC
    if val=="Cluster":
        return ReasonType.CLUSTER
    if val=="ClusterHead":
        return ReasonType.CLUSTER_HEAD
    return ReasonType.UNKNOWN

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

class ReasonHead():
    """a reason head has a delay and may have several subreasons"""
    def __init__(self, type_of, identifier):
        self._type = type_of
        self._id = identifier
        self._delay = ""
        self._end_tp = ""
        self._subreasons = []

    def __str__(self):
        msg = "Reason type=%s id=%s tp=%s delay=%s #sub=%d" % \
            (self._type, self._id, self._end_tp, self._delay, len(self._subreasons))
        return msg

    def add_delay(self, delay):
        self._delay = reformat_timestring(delay)

    def add_end_timepoint(self, timepoint):
        self._end_tp = timepoint

    def add_subreason(self, subreason):
        self._subreasons.append(subreason)

class SubReason():
    """one reason (structure, timebound, material, resource, mat_res, res_res"""
    def __init__(self, type_of, time_late, process):
        self._type = type_of
        self._time_late = time_late
        self._process = process

    def __str__(self):
        msg = "sub_reason type=%s time_late=%s" % (self._type, self._time_late)
        return msg

class RegressionReasons:
    """regression result textfile pair based on a message file"""
    def __init__(self, reference_file):
        self.reference_file = reference_file

    def __str__(self):
        msg = "RegressionReasons\n\tref='%s'\n\tres='%s'\n\t%d" % \
            (self.get_reference_file(), self.get_result_file(), self.get_result())
        return msg

    def get_reference_file(self):
        return self.reference_file
    def get_result_file(self):
        return RegressionUtil.get_result_file(self.reference_file)

    def get_result(self):
        res = self.get_result_file()
        if res is None:
            return Regr.FAILED
        return self.compare(self.get_reference_file(), res)

    def compare(self, ref, res):
        return Regr.OK if filecmp.cmp(ref, res) else Regr.DIFF


def get_reasons(reason_file):
    reasons = []
    rgx_start = re.compile(r'^(Cluster|ClusterHead|PartProcess)=(.*)$')
    rgx_delay = re.compile(r'\sdelay=(\S+)')
    rgx_endtime = re.compile(r'\send_time=(\S+)')
    rgx_subreason = re.compile(r'reason=(\S+).*timeLate=(\S+).*process=([^=]*\S)(?:$|\s+\S+=)')
    new_reason = None
    new_subreason = None
    for line in open(reason_file):
        hit = rgx_start.search(line)
        if hit:
            if new_subreason is not None:
                new_reason.add_subreason(new_subreason)
            new_subreason = None
            if new_reason is not None:
                reasons.append(new_reason)
            new_reason = ReasonHead(to_reason_type(hit.group(1)), hit.group(2))
            continue
        hit = rgx_subreason.search(line)
        if hit:
            if new_subreason is not None:
                new_reason.add_subreason(new_subreason)
            new_subreason = SubReason(*hit.groups())
            continue
        hit = rgx_delay.search(line)
        if hit:
            new_reason.add_delay(hit.group(1))
        hit = rgx_endtime.search(line)
        if hit:
            new_reason.add_end_timepoint(hit.group(1))

    return reasons

def parse_arguments():
    """parse commandline arguments"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('reference_file', metavar='reference_file', help='input regression reference file')
    return parser.parse_args()

def main():
    """main function"""
    args = parse_arguments()

    item = RegressionReasons(args.reference_file)
    print(item)
    reasons = get_reasons(args.reference_file)
    print("#reason=%d\n\n" % len(reasons))
    for item in reasons:
        print(item)

if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
