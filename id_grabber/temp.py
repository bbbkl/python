# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: temp.py
#
# description
"""\n\n
    script to try something out and which is not lost after shutdown
"""

import re
import os.path
from argparse import ArgumentParser
import sys
from glob import glob

VERSION = '0.1'


def test_encoding(message_file):
    """check for file encoding"""
    encodings = ["UTF-8", "ISO-8859-1", "latin-1"]
    
    if not os.path.exists(message_file):
        raise FileNotFoundError(message_file)
    
    for item in encodings:
        try:
            for line in open(message_file, encoding=item):
                pass
            return item
        except:
            pass
        
    raise ("Cannot get right encoding, tried %s" % str(encodings))

def show_traffic(filename):
    rgx = re.compile('(DEF_APS\S+)')
    traffic = {}
    for line in open(filename):
        hit = rgx.search(line)
        if hit:
            cmd = hit.group(1)
            traffic.setdefault(cmd, 0)
            traffic[cmd] += 1
    
    cnt2Cmd = {}
    for cmd in traffic:
        cnt = traffic[cmd]
        cnt2Cmd.setdefault(cnt, [])
        cnt2Cmd[cnt].append(cmd)
        
    for cnt in sorted(cnt2Cmd):
        for cmd in cnt2Cmd[cnt]:
            print("%s %d" % (cmd, cnt))
    
    
def is_ascii(text):
    return all(ord(c) < 128 for c in text)

def ascii_check(filename):
    encoding_id = test_encoding(filename)
    
    for i, line in enumerate(open(filename, encoding=encoding_id)):
        try:
            if not is_ascii(line):
                print("non ascii line %d, '%s'" % (i, line))
        except:
            print("check line %d" % i)
            pass
    
def command_check(filename):
    encoding_id = test_encoding(filename)
    last_num = -1
    for i, line in enumerate(open(filename, encoding=encoding_id)):
        found_num = -1
        if line.find('2') == 0:
            found_num = 2
        if line.find('1\t2') == 0:
            found_num = 2
        if line.find('1\t3') == 0:
            found_num = 3
        if line.find('3') == 0:
            found_num = 3 
        if found_num != -1:
            if found_num == last_num:
                print("OOps, %d occurs twice, line %d" % (last_num, i))
            last_num = found_num    
    
def get_duration(tp1, tp2):
    #print("tp1=%s tp2=%s" % (tp1, tp2))
    rgx = re.compile('(\d{2})\:(\d{2})\:(\d{2})\.(\d)')
    h1, m1, s1, mm1 = [int(x) for x in rgx.match(tp1).groups()]
    h2, m2, s2, mm2 = [int(x) for x in rgx.match(tp2).groups()]
    diff = ((h2 * 60 + m2) * 60 + s2) * 1000 + mm2 - ((h1 * 60 + m1) * 60 + s1) * 1000 + mm1
    return diff
        
    
def check_connect_times(filename, dt2durations):
    found_flag = False
    rgx_key =  re.compile(r'^\[([0-9/]+)@(\d{2}\:\d{2}\:\d{2}\.\d+).*Return from calcStartup')
    rgx_time = re.compile(r'^\[([0-9/]+)@(\d{2}\:\d{2}\:\d{2}\.\d+)')
    dt1 = tp1 = tp2 = ""
    for line in open(filename):
        if found_flag:
            hit = rgx_time.search(line)
            tp2 = hit.group(2)
            print(line[:-1])
            good_flag = line.find('Run getConnectionMetaData')!=-1
            duration = get_duration(tp1, tp2)
            dt2durations.setdefault(dt1, {})
            durations = dt2durations[dt1]
            durations.setdefault('bad', set())
            durations.setdefault(duration, [])
            durations[duration].append(tp1)
            if not good_flag:
                durations['bad'].add(duration)
            print("duration=%d %s" % (duration, "" if good_flag else "xxx"))
            print("---------------------------------------")
            found_flag = False
            continue
        hit = rgx_key.search(line)
        if hit:
            dt1 = hit.group(1)
            tp1 = hit.group(2)
            print(line[:-1])
            found_flag = True
            
    #return  dt2durations       
    """
    print("duration statistic:")
    for day in sorted(dt2durations):
        print("Date: %s" % day)
        durations = dt2durations[day]
        for duration in sorted(durations):
            
            suffix = "xxx" if duration in bad_durations else "   "
            start_tp = ' '.join(durations[duration])
            print("% 7d:    % 3d %s %s" %(duration, len(durations[duration]), suffix, start_tp))
    """
    
def pretty_print(dt2durations):
    print("duration statistic:")
    for day in sorted(dt2durations):
        print("Date: %s" % day)
        durations = dt2durations[day]
        bad_durations = durations['bad']
        del durations['bad']
        for duration in sorted(durations):
            suffix = "xxx" if duration in bad_durations else "   "
            start_tp = ' '.join(durations[duration])
            print("% 7d:    % 3d %s %s" %(duration, len(durations[duration]), suffix, start_tp))  
     
def get_durations(duration_file):
    durations = {}
    for line in open(duration_file):
        hit = re.search('^duration=(\d+)', line)
        if hit:
            duration = int(hit.group(1))
            durations.setdefault(duration, 0)
            durations[duration] += 1
    for duration in sorted(durations):
        print("% 7d:    % 3d" %(duration, durations[duration]))
    
def lookup_logfiles(start_dir):
    stat_data = {}
    extensions = ('.log')
    for root, dirs, files in os.walk(start_dir):
        relevant_files = list(filter(lambda x: os.path.splitext(x)[1] in extensions, files))
        for fn in relevant_files:
            #loc = loc + count_lines(os.path.join(root, fn))
            check_connect_times(os.path.join(root, fn), stat_data)    
    pretty_print(stat_data)
    
def make3rd(filename1, filename2):
    out = open(filename1 + "_combinded.csv", "w")
    lines1 = open(filename1).readlines()
    lines2 = open(filename2).readlines()
    print("cnt1=%d, cnt2=%d" % (len(lines1), len(lines2)))
    nextValidIdx = -1
    for idx, line in enumerate(lines1):
        key = line[:-1]
        if idx <= nextValidIdx:
            continue
        if key == "":
            out.write(line)
            out.write(line)
        else:
            print(lines2[idx])
            print(lines2[idx+1])
            print(lines2[idx+2])
            out.write(line)
            out.write(lines1[idx+1])
            out.write(lines2[idx+2])
            nextValidIdx = idx+3
            print("idx=%s, nextValid=%d" % (idx, idx+3))
            
    out.close()
    
def parse_joblogs(directory):
    """parse all job logs ..."""
    joblogs = glob(directory + "/*.txt")
    rgx = re.compile('^\s+(\d+)\:\s+(\d+)') 
    for item in joblogs:
        cnt = 0
        id = os.path.basename(item).replace('.txt', '').replace('jobs_', '')
        print('\n%s' % id)
        for line in open(item):
            hit = rgx.search(line)
            if hit:
                print("%s\t%s" % (hit.group(1), hit.group(2)))
                cnt += 1
            if cnt >= 3:
                break
    
def grep_zzz(filename):
    rgx = re.compile(r'(xxx.*)')    
    for line in open(filename):
        hit = rgx.search(line)
        if hit:
            print(hit.group(1))
    
def sendMail():
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    address_book = [ 'bernd.krueger@proalpha.de', ] #'jens.leoff@proalpha.de', 'robert.wagner@proalpha.de']
    msg = MIMEMultipart()    
    sender = 'Jenkins.PPS@proalpha.de'
    subject = "Vielen Dank - '10.1.0.62' war der Missing Link!"
    body = "thx" 
    """
    def sendMail():
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    address_book = ['bernd.krueger@proalpha.de', 'jens.leoff@proalpha.de', 'robert.wagner@proalpha.de']
    msg = MIMEMultipart()    
    sender = 'Jenkins.PPS@proalpha.de'
    subject = "My subject"
    body = "This is my email body"
    
    msg['From'] = sender
    msg['To'] = ','.join(address_book)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    text=msg.as_string()
    #print text
    # Send the message via our SMTP server
    s = smtplib.SMTP('10.1.0.62')
    s.sendmail(sender,address_book, text)
    s.quit()   
    """
    
    msg['From'] = sender
    msg['To'] = ','.join(address_book)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    text=msg.as_string()
    #print text
    # Send the message via our SMTP server
    s = smtplib.SMTP('10.1.0.62')
    s.sendmail(sender,address_book, text)
    s.quit()           
    
def show_strange_lines(filename):
    idx = 0
    rgx = re.compile('^\\d\t')
    for line in open(filename):
        idx += 1
        if not rgx.search(line):
            print("%d '%s'" % (idx, line))
       
    
def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('message_file', metavar='message_file', help='input message file')
    parser.add_argument('-m', '--mat-id', metavar='string', # or stare_false
                      dest="id_mat", default='', # negative store value
                      help="material id to grep")
    parser.add_argument('-c', '--count', metavar='N', type=int, # or stare_false
                      dest="count", default=0, # negative store value
                      help="count")
    parser.add_argument('-p', '--pattern', metavar='string', # or stare_false
                      dest="pattern", default='xxx', # negative store value
                      help="search pattern within logfile")
    return parser.parse_args()        
        
def main():
    """main function"""
    args = parse_arguments()
    filename = args.message_file
    
    show_strange_lines(filename)
    
    #show_traffic(filename)
    #ascii_check(filename)
    #command_check(filename)
    #result = {}
    #check_connect_times(filename, result)
    #pretty_print(result)
    #get_durations(filename)

    
    #lookup_logfiles(filename)

    #f1 = sys.argv[1]
    #f2 = sys.argv[2]
    #make3rd(f1, f2)
    
    #grep_zzz(sys.argv[1])
    #sendMail()



if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
