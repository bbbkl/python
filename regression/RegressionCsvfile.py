# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: RegressionCsvfile.py
#
# description
"""\n\n
    regression csv file pair reference/result
"""

from argparse import ArgumentParser
import os.path
import re
from glob import glob

VERSION = '1.0'

class RegressionCsvfile:
    """regression csv pair based on a message file"""
    def __init__(self, reference_file):
        self.reference_file = reference_file
    
    def __str__(self):
        msg = "RegressionCsvfile (%s)\n\tref='%s'\n\tres='%s'\n\t%d" % \
            (self.get_type(), self.get_reference_file(), self.get_result_file(), self.get_result())
        return msg
    
    def get_reference_file(self):
        return self.reference_file
    def get_result_file(self):
        basename = os.path.basename(self.reference_file)
        basename = basename.replace('reference', 'result')
        hit = re.search('(_\d{8}_\d{6})[^\d]', basename)
        if hit:
            candidates = glob(os.path.join(os.path.dirname(self.reference_file), basename.replace(hit.group(1), '*')))
            rgx = re.compile(basename.replace(hit.group(1), r'_\d{8}_\d{6}'))
            for item in candidates:
                if rgx.search(item):
                    return item              
        return None

    def is_headproc(self):
        return self.reference_file.find('.headproc_reference.csv') != -1 and not self.is_ctp()
    def is_partproc(self):
        src = self.reference_file
        return src.find('.reference.csv') != -1 and not self.is_ctp()
    def is_activity(self):
        return self.reference_file.find('.activities') != -1
    def is_ctp(self):
        return re.search(r'_ctp\d{4}', self.reference_file)
    
    def get_type(self):
        if self.is_headproc():
            return "headproc"#
        if self.is_partproc():
            return "partproc"
        if self.is_activity():
            return "activity"
        if self.is_ctp():
            return "ctp"
        return "_unknown_"

    def get_result(self):
        res = self.get_result_file()
        if res is None:
            if self.is_activity():
                return 1 # activity csv file is not mandatory
            return 0
        return self.compare(self.get_reference_file(), res)
    
    def compare(self, ref, res):
        ref_lines = [x.rstrip() for x in open(ref).readlines() if x.rstrip()]
        res_lines = [x.rstrip() for x in open(res).readlines() if x.rstrip()]
        if len(ref_lines) != len(res_lines):
            return 0
        for line in ref_lines:
            if res_lines.count(line) == 0:
                return 0
        return 1

def parse_arguments():
    """parse commandline arguments"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION    
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('reference_file', metavar='reference_file', help='input regression reference logfile')
    return parser.parse_args()

def main():
    """main function"""
    args = parse_arguments()

    item = RegressionCsvfile(args.reference_file)
    print(item)
        
if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
