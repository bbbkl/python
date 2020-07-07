# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: RegressionReasons.py
#
# description
"""\n\n
    regression reason text file pair reference/result
"""

from argparse import ArgumentParser
import filecmp
import re
from RegressionResultCodes import Regr
import RegressionUtil

VERSION = '1.0'

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

if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
