# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: RegressionMessage_file.py
#
# description
"""\n\n
    regression message file and related reference/result logfiles
"""

from argparse import ArgumentParser
from RegressionLogfile import RegressionLogfile
from RegressionCsvfile import RegressionCsvfile
from RegressionException import RegressionException
from glob import glob
import os.path
import re
import sys

VERSION = '1.0'

class RegressionMessagefile:
    """regression configuration based on a configuration file"""
    def __init__(self, message_file):
        self.message_file = message_file
        self.logfile_pair = RegressionLogfile(self.get_reference_logfile(message_file))
        self.headproc_pair = None
        self.partproc_pair = None
        self.activitities_pair = None
        self.ctp_pairs = []
        self.get_csvfiles(message_file)
        
    def __str__(self):
        if 0:
            msg = "Regressionmessage_file %d '%s'" % (self.get_result(), self.message_file)
            msg += "\n%s" % self.logfile_pair
            msg += "\n%s" % self.headproc_pair
            msg += "\n%s" % self.partproc_pair
            if self.activitities_pair:
                msg += "\n%s" % self.activitities_pair
            for item in self.ctp_pairs:
                msg += "\n%s" % item
            return msg
        else:
            return self.create_report()
    
    def create_report(self):
        """create report for mail"""
        report = os.path.basename(self.message_file)
        report +=  " ok " if self.get_result() else " ***not ok*** "
        report += self.logfile_pair.create_report()
        for item in self.get_items():
            if item.get_result() != 1:
                report += "\n\t%s" % item.get_reference_file()
                report += "\n\t%s" % item.get_result_file()
        return report
        
    def get_items(self):
        result = [self.logfile_pair,]
        for item in [self.headproc_pair, self.partproc_pair, self.activitities_pair]:            
            if item:
                result.append(item)
        result.extend(self.ctp_pairs)
        return result
    
    def get_result(self):
        for item in self.get_items():
            if item.get_result() == 0:
                return 0
        return 1
    
    def get_messagefile(self):
        return self.message_file
    
    def get_reference_logfile(self, message_file):
        basename = os.path.basename(message_file)
        logname = os.path.basename(message_file)[:-3] + "reference.log" 
        pattern = message_file.replace(basename, "*%s" % logname)
        candidates = glob(pattern)
        if len(candidates) != 1:
            raise RegressionException("cannot figure out reference logfile for message file '%s'" % message_file)
        return candidates[0]
    
    def rename_result_logfile(self):
        message_file = self.get_messagefile()
        dst = self.get_reference_logfile(message_file).replace('.reference.log', '.result.log')
        if os.path.exists(dst):
            return
        basename = os.path.basename(message_file)
        logname = os.path.basename(message_file)[:-3] + "log" 
        pattern = message_file.replace(basename, "*%s" % logname)
        candidates = glob(pattern)
        candidates = [x for x in candidates if x.find(".reference.log") == -1]
        if len(candidates) != 1:
            raise RegressionException("cannot figure out result logfile for message file '%s'" % message_file)
        src = candidates[0]
        dst = self.get_reference_logfile(message_file).replace('.reference.log', '.result.log')
        os.rename(src, dst)
        
    def get_csvfiles(self, message_file):
        basename = os.path.basename(message_file)[:-4]
        rgx = re.compile(r".*%s_\d{8}_\d{6}.*reference\.csv$" % basename)
        base = message_file[:-4]
        candidates = glob(base + "*reference.csv")
        for item in candidates:
            hit = rgx.search(item)
            if hit:
                csvItem = RegressionCsvfile(item)
                if csvItem.is_headproc():
                    self.headproc_pair = csvItem
                elif csvItem.is_partproc():
                    self.partproc_pair = csvItem
                elif csvItem.is_activity():
                    self.activitities_pair = csvItem
                elif csvItem.is_ctp():
                    self.ctp_pairs.append(csvItem)
                else:
                    print("xxx UNHANDLED csv file", csvItem)

def parse_arguments():
    """parse commandline arguments"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION    
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('message_file', metavar='message_file', help='input regression message file')
    return parser.parse_args()

def main():
    """main function"""
    args = parse_arguments()

    regression_item = RegressionMessagefile(args.message_file)
    #regression_item.rename_result_logfile()
    print(regression_item)
        
if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
