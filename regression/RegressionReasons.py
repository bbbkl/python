# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: RegressionReasons.py
#
# description
"""\n\n
    regression reason text file pair reference/result

    do reason compare only if process endtimes of whole set did not change,
    otherwise we compare onions which apples.
    This must be checked by framework before.

    check whether body file for reference exists, if not -> OK
    get ref_reason_set
    get res_reason_set

    compare:
    - number of ReasonHead equal?
    - for each ReasonHead pair:
      - same endtime (sanity check)
      - equal number of subreasons?
"""

from argparse import ArgumentParser
from enum import IntEnum
import filecmp
import re
from RegressionResultCodes import Regr
from RegressionException import RegressionReasonException
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

class ReasonSet():
    """all reasons of one reason textfile"""
    def __init__(self, identifier):
        self._id = identifier
        self._reasons = {}

    def add_reason(self, reason):
        key = reason.get_key()
        if key in self._reasons:
            raise RegressionReasonException("reason key=%s occurs twice" % key)
        self._reasons[key] = reason

    def contains_reason(self, key):
        return key in self._reasons

    def get_reason(self, key):
        if key in self._reasons:
            return self._reasons[key]
        return None

    def compare(self, other):
        """compare against another reason set"""
        if len(self._reasons) != len(other._reasons):
            return Regr.DIFF
        for key, ref_reason in self._reasons.items():
            res_reason = other.get_reason(key)
            if res_reason is None or ref_reason != res_reason:
                return Regr.DIFF
        return Regr.OK


class ReasonHead():
    """a reason head has a delay and may have several subreasons"""
    def __init__(self, type_of, identifier):
        self._type = type_of
        self._id = identifier
        self._delay = ""
        self._end_tp = ""
        self._subreasons = {}

    def __str__(self):
        msg = "Reason type=%s id=%s tp=%s delay=%s #sub=%d" % \
            (self._type, self._id, self._end_tp, self._delay, len(self._subreasons))
        return msg

    def get_key(self):
        key = "%s id=%s" % (self._type, self._id)
        if self.is_mat_proxy():
            key += " mat=%s" % self.get_material()
        return key

    def is_mat_proxy(self):
        return self._id.find("fixed_mat") != -1

    def get_material(self):
        if len(self._subreasons) > 1:
            raise RegressionReasonException("fixed_mat proxy reason with not exactly one sub reason, id=%s" % self._id)
        for key in self._subreasons:
            return self._subreasons[key].get_id()

    def add_delay(self, delay):
        self._delay = reformat_timestring(delay)

    def add_end_timepoint(self, timepoint):
        self._end_tp = timepoint

    def add_subreason(self, subreason):
        key = subreason.get_key()
        if key in self._subreasons:
            if subreason.get_timebound() is not None:
                print("INFO subreason key=%s occurs twice" % key)
                return
            raise RegressionReasonException("subreason key=%s occurs twice" % key)
        self._subreasons[key] = subreason

    def get_subreason(self, key):
        if key in self._subreasons:
            return self._subreasons[key]
        return None

    def __eq__(self, other):
        if self._end_tp != other._end_tp:
            return 0
        if len(self._subreasons) != len(other._subreasons):
            return 0
        for key, subreason in self._subreasons.items():
            res_subreason = other.get_subreason(key)
            if res_subreason is None or subreason != res_subreason:
                return 0
        return 1

class SubReason():
    """one reason (structure, timebound, material, resource, mat_res, res_res"""
    def __init__(self, type_of, time_late, process):
        self._type = type_of
        self._time_late = time_late
        self._process = process
        self._timebound = None
        self._id = None

    def get_key(self):
        return "%s proc=%s tb=%s id=%s" % (self._type, self._process, self._timebound, self._id)

    def set_id(self, val):
        self._id = val
    def get_id(self):
        return self._id
    def add_timebound(self, timebound, act):
        self._id = "%s/%s" % (timebound, act)
        self._timebound = timebound
    def add_precedence_acts(self, act1, act2):
        self._id = "%s;%s" % (act1, act2)

    def get_timebound(self):
        return self._timebound

    def __str__(self):
        msg = "sub_reason type=%s time_late=%s" % (self._type, self._time_late)
        return msg

    def __eq__(self, other):
        if self._time_late != other._time_late:
            return 0
        return 1


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
        res_file = self.get_result_file()
        if res_file is not None:
            if filecmp.cmp(self.get_reference_file(), res_file):
                return Regr.OK
            ref = get_reasons(self.get_reference_file())
            res = get_reasons(res_file)
            return ref.compare(res)
        return Regr.OK


def get_reason_identifier(line):
    """get reason specific identifier (material, resource, timebound ..."""
    regex = [
        r'resource1=(\S+).*ress?ource2=(\S+)', # combi res_res
        r'material=(\S+).*resource=(\S+)', # combi mat_res
        r'resource=([^=]+)\s+\S+=',  # resource=xyz K3 (Machine) timeLate=P0
         r'material=([^=]+)\s+\S+='] # mat

    for rgx in regex:
        hit = re.search(rgx, line)
        if hit:
            return '/'.join(hit.groups())
    return None

def get_reasons(reason_file):
    try:
        reasons = ReasonSet(reason_file)
        rgx_start = re.compile(r'^(Cluster|ClusterHead|PartProcess)=(.*)$')
        rgx_delay = re.compile(r'\sdelay=(\S+)')
        rgx_endtime = re.compile(r'\send_time=(\S+)')
        rgx_subreason = re.compile(r'reason=(\S+).*timeLate=(\S+).*process=([^=]*\S)(?:$|\s+\S+=)')
        rgx_timebound = re.compile(r'act=(?: name=)?([^=]+)\s+\S+=.*timeBound=(\S+)')
        rgx_precedence = re.compile(r'fromAct=(\S+)\s+toAct=(\S+)')
        new_reason = None
        new_subreason = None
        for line in open(reason_file, encoding=RegressionUtil.test_encoding(reason_file)) :
            hit = rgx_start.search(line)
            if hit:
                if new_subreason is not None:
                    new_reason.add_subreason(new_subreason)
                new_subreason = None
                if new_reason is not None:
                    if new_reason.is_mat_proxy() and not reasons.contains_reason(new_reason.get_key()):
                        reasons.add_reason(new_reason)
                new_reason = ReasonHead(to_reason_type(hit.group(1)), hit.group(2))
                continue
            hit = rgx_subreason.search(line)
            if hit:
                if new_subreason is not None:
                    new_reason.add_subreason(new_subreason)
                new_subreason = SubReason(*hit.groups())
                identifier = get_reason_identifier(line)
                if identifier is not None:
                    new_subreason.set_id(identifier)
                continue
            hit = rgx_delay.search(line)
            if hit:
                new_reason.add_delay(hit.group(1))
            hit = rgx_endtime.search(line)
            if hit:
                new_reason.add_end_timepoint(hit.group(1))
            if line.find('timeBound') != -1:
                hit = rgx_timebound.search(line)
                if hit:
                    new_subreason.add_timebound(hit.group(1), hit.group(2))
            if line.find('precedence_delay') != -1:
                hit = rgx_precedence.search(line)
                if hit:
                    new_subreason.add_precedence_acts(hit.group(1), hit.group(2))

        return reasons
    except RegressionReasonException as ex:
        raise RegressionReasonException("%s, file %s" % (ex, reason_file))

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
    
    print("\nreason compare result = %s" % item.get_result())

if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
