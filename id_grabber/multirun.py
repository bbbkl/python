# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: multirun.py
#
# description
import cmd
"""\n\n
    script to try something out and which is not lost after shutdown
"""

import re
import os.path
from argparse import ArgumentParser
from subprocess import run
import shutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

VERSION = '0.1'

class MultirunConfig:
    def __init__(self, args):
        self.exe_src = ''
        self.exe_dst = ''
        self.params = ''
        self.messagefile = ''
        self.optsrv_ini = ''
        self.workdir = ''
        self.recipients = ''
        self.turns = 10

        if os.path.exists(args.config):
            self.parse_config(args.config)
            
        if args.exe_src:
            self.exe_src = args.exe_src
        if args.exe_dst:
            self.exe_dst = args.exe_dst

    def keys(self):
        return ['exe_src', 'exe_dst', 'params', 'messagefile', 'optsrv_ini', 'workdir', 'recipients', 'turns']

    def __str__(self):
        msg = ""
        for key in self.keys():
            msg += "%s=%s\n" % (key, eval('self.%s' % key))
        return msg

    def parse_config(self, configfile):
        for line in open(configfile):
            for key in self.keys():
                hit = re.search('^' + key + "=(.*)", line)
                if hit:
                    val = hit.group(1)
                    if val.find('#') != -1:
                        val = val[:val.index('#')]
                    self.__dict__[key] = val.rstrip()
                    break 

def prepare_workdir(workdir_base):
    wdir = workdir_base + "/multirun_wdir"
    wdir_old = wdir + ".old"
    if os.path.isdir(wdir):
        os.rename(wdir, wdir_old)
        shutil.rmtree(wdir_old)
    os.makedirs(wdir)
    return wdir

def prepare_executable(exe_src, exe_dst):
    if os.path.exists(exe_src):
        shutil.copyfile(exe_src, exe_dst)

def do_multirun(config):
    prepare_executable(config.exe_src, config.exe_dst)
    workdir = prepare_workdir(config.workdir)
    cmd = "%s %s -offline -w %s -TestMessage %s" % (config.exe_dst, config.params, workdir, config.messagefile)
    filename_output = workdir + "/memtest.output.txt"
    with open(filename_output, "w") as stream:
        for turn in range(config.turns):
            print("\nmultirun turn %d\n" % (turn + 1))
            stream.write("\n\nmultirun turn %d\n\n" % (turn + 1))
            stream.flush()
            result = run(cmd, stdout=stream)
            stream.write("\n\nmultirun result=%d\n\n" % result.returncode)
            stream.flush()
            if result.returncode == 0:
                return
                
    subject = "Memcheck multirun failed"
    text = ''.join(open(filename_output).readlines())
    mail_result(subject, text, config.recipients)
    
    print("multirun result return code=%s" % result.returncode)
    
def write_testrunner_result(filename, result):
    with open(filename, "w") as stream:
        stream.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        stream.write('<testsuites tests="1" failures="%d" disabled="0" errors="0" timestamp="2018-08-21T15:44:33" time="0" name="AllTests">\n' % result)
        stream.write('<testsuite name="MemoryTestSuite" tests="1" failures="%d" disabled="0" errors="0" time="0">' % result)
        stream.write('<testcase name="memcheck" status="run" time="0" classname="MemoryTest" />')
        stream.write('</testsuite>\n</testsuites>\n')    

def mail_result(subject, text, recipients):
    """mail given subject / text to recipients, provided as comma separated list"""
    if not recipients:
        return
    address_book = recipients.split(',') #['bernd.krueger@proalpha.de', 'jens.leoff@proalpha.de', 'robert.wagner@proalpha.de']
    msg = MIMEMultipart()    
    sender = 'Jenkins.PPS@proalpha.de'
    body = text
    
    msg['From'] = sender
    msg['To'] = ','.join(address_book)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    text=msg.as_string()
    s = smtplib.SMTP('10.1.0.62')
    s.sendmail(sender,address_book, text)
    s.quit()

def multirun_csv(filename):
    """grep csv relevant values out of given multirun output file"""
    rgx = re.compile(r'peak_mem=(\d+\.\d+).*curr_mem=(\d+\.\d+).*duration=(\d+\.\d+).*')
    fn_out = filename + '.csv'
    out = open(fn_out, 'w')
    out.write("PEAK_MEM;CURR_MEM;DURATION\n")
    for line in open(filename):
        hit = rgx.search(line)
        if hit:
            pm, cm, dur = map(lambda x: x.replace('.', ','), hit.groups())
            out.write('%s;%s;%s\n' % (pm, cm, dur))
    out.close()
    print("output file is %s " % fn_out)
        
def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    #parser.add_argument('memory_usage_file', metavar='memory_usage_file', help='input memory usage file')
    parser.add_argument('-cfg', '--config', metavar='string',
                        dest='config', default='', 
                        help="parse given multirun config file")
    parser.add_argument('--exe_src', metavar='string',
                        dest='exe_src', default='', help="source executable to use")
    parser.add_argument('--exe_dst', metavar='string',
                        dest='exe_dst', default='', help="destination executable to use")

    return parser.parse_args()        
        
def main():
    """main function"""
    args = parse_arguments()
    
    #filename = args.memory_usage_file
    #multirun_csv(filename)
    
    config = MultirunConfig(args)   
    print(config) 
    do_multirun(config)
    
if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
