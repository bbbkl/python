# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: regression.py
#
# description
"""\n\n
    regression util functions
"""

import sys
import os
import shutil
import datetime
from argparse import ArgumentParser
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from subprocess import run
from RegressionConfig import RegressionConfig
from RegressionMessagefile import RegressionMessagefile
from RegressionException import RegressionException

VERSION = '1.0'

class Regression:
    """main regression class, which perforce a regression"""
    def __init__(self, regression_id, configuration_file):
        self.regression_id = regression_id
        self.config = RegressionConfig(configuration_file)
        self.regression_dir = None
        self.regression_messagefiles = []
        
    def get_id(self):
        return self.regression_id
    
    def get_report_file(self):
        return os.path.join(self.regression_dir, "regression_report.txt")
    
    def get_stdout_file(self):
        return os.path.join(self.regression_dir, "regression.stdout.txt")
    
    def create_report(self):
        """create report for mail"""
        report = "number of messagefiles=%d\n" % len(self.regression_messagefiles)
        for item in self.regression_messagefiles:
            report += "\n" + item.create_report() + "\n"
        return report
    
    def get_result(self):
        for item in self.regression_messagefiles:
            if item.get_result() == 0:
                return 0
        return 1
    
    def copy_regression_exe(self):
        if os.path.exists(self.config.get_src_exe()):
            shutil.copyfile(self.config.get_src_exe(), self.config.get_regression_exe())

    def do_regression(self):
        self.copy_regression_exe()
        config = self.config
        self.regression_dir = self.create_regression_dir(config.get_reference_dir())
        self.set_messagefiles(self.regression_dir)
        duration = self.call_optimizer(config.get_regression_exe(), config.get_params(), self.regression_messagefiles)
        self.check_and_publish_regression_result(duration)

    def set_messagefiles(self, regression_dir):
        """for each *.dat file within regression dir create one RegressionMessageFile"""
        for root, dirs, files in os.walk(regression_dir):
            for item in [x for x in files if os.path.splitext(x)[-1].lower() == '.dat']:
                msg = os.path.join(root, item)
                self.regression_messagefiles.append(RegressionMessagefile(msg))

    def create_regression_dir(self, reference_dir):
        """for given reference dir, create regression dir with symlinks to save disk space"""
        regression_dir = self.get_new_regression_dir(reference_dir)
        for root, dirs, files in os.walk(reference_dir):
            dst_root = root.replace(reference_dir, regression_dir)
            for item in dirs:
                dst = os.path.join(dst_root, item)
                os.makedirs(dst)
            for item in files:
                src = os.path.join(root, item)
                dst = os.path.join(dst_root, item)
                os.symlink(src, dst)
        return regression_dir

    def get_new_regression_dir(self, reference_dir):
        """get new directory name with refernce_dir as prefix, add unique suffix"""
        if not os.path.isdir(reference_dir):
            sys.exit("dir does not exist: get_new_regression_dir requires existing directory as input (input was '%s')" % reference_dir)
        base = reference_dir + datetime.datetime.now().strftime("_%Y%m%d")
        idx = 0
        while True:
            dst = base + ".%02d" % idx
            if not os.path.isdir(dst):
                os.makedirs(dst)
                return dst
            idx += 1

    def call_optimizer(self, exe, params, message_files):
        """call optimizer for each message file, return elapsed time"""
        duration = datetime.datetime.now() - datetime.datetime.now()
        for message_file in message_files:
            msgfile = message_file.get_messagefile()
            workdir = os.path.dirname(msgfile)
            cmd = '%s -offline %s -w %s -TestMessage %s' % (exe, params, workdir, msgfile)
            time_start = datetime.datetime.now()
            with open(self.get_stdout_file(), "a") as outstream:
                outstream.write("\n\n--- handline message %s ---\n\n" % message_file.get_messagefile())
            with open(self.get_stdout_file(), "a") as outstream:
                run(cmd, stdout=outstream, stderr=outstream)
            time_end = datetime.datetime.now()
            duration += time_end - time_start
            message_file.rename_result_logfile()
            with open(self.get_report_file(), "a") as report:
                report.write("\n%s\n" % message_file.create_report())
        return duration

    def check_and_publish_regression_result(self, duration):
        """check combined result of all message files, create regression report, mail it"""
        subject = "regression %s: " % self.get_id()
        subject += "ok" if self.get_result() == 1 else "failed"
        subject += "   elapsed_time %s" % duration
        body = self.regression_dir 
        body += "\n\n"
        body += self.create_report()
        send_regression_mail(subject, body, self.config.get_recipients())

def send_regression_mail(subject, text, recipients):
    """mail given subject / text to recipients, provided as comma separated list"""
    if not recipients:
        return
    address_book = recipients.split(',') #['bernd.krueger@proalpha.de', 'jens.leoff@proalpha.de', 'robert.wagner@proalpha.de']
    msg = MIMEMultipart()    
    sender = 'Jenkins.PPS@proalpha.de'
    body = text + '\n\nto enable/activate symlinks on your machine, please type:\n\tfsutil behavior set SymlinkEvaluation R2R:1'
    
    msg['From'] = sender
    msg['To'] = ','.join(address_book)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    text=msg.as_string()
    s = smtplib.SMTP('10.1.0.62')
    s.sendmail(sender,address_book, text)
    s.quit()

def parse_arguments():
    """parse commandline arguments"""
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('regression_id', metavar='regression_id', help='regression id')
    parser.add_argument('config_file', metavar='config_file', help='input regression configuration file')
    """
    parser.add_argument('--regression_dir', metavar='regression_dir',
                        dest="regression_dir", default='', 
                        help="full path of regression dir")
    parser.add_argument('--regression_dir', metavar='regression_dir',
                        dest="regression_dir", default='', 
                        help="full path of regression dir")
    parser.add_argument('--recipients', metavar='recipients', dest='recipients', default='',
                        help="comma separated list of email recipients")
                        """
    return parser.parse_args()

def main():
    """main function"""
    args = parse_arguments()

    try:
        regression = Regression(args.regression_id, args.config_file)
        regression.do_regression()
    except RegressionException as ex:
        print(ex)
        raise ex
    return
        
if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
