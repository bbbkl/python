# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: RegressionUtil.py
#
# description
"""\n\n
    regression util functions
"""
import ctypes
import os.path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import re
from glob import glob

def get_result_file(reference_file):
    """for given reference file find corresponding result file"""
    replacements = { 'reference' : 'result', 'reference.' : ''}
    for key, replacment in replacements.items():
        basename = os.path.basename(reference_file)
        basename = basename.replace(key, replacment)
        hit = re.search(r'(_\d{8}_\d{6})[^\d]', basename)
        if hit:
            candidates = glob(os.path.join(os.path.dirname(reference_file), basename.replace(hit.group(1), '*')))
            rgx = re.compile(basename.replace(hit.group(1), r'_\d{8}_\d{6}'))
            for item in candidates:
                if rgx.search(item):
                    return item
    return None

def is_admin():
    """return true if we have admin rights, false otherwise"""
    try:
        res = ctypes.windll.shell32.IsUserAnAdmin() != 0
    except AttributeError:
        #res = os.getuid() == 0 # non windows
        pass
    return res

def send_regression_mail(subject, text, recipients,develop=False):
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
    if develop:
        print("mail from=%s" % msg['From'])
        print("mail to=%s" % msg['To'])
        print("subject=%s" % msg['Subject'])
        print("body=%s" % body)
        return
    smtp = smtplib.SMTP('10.1.0.62')
    smtp.sendmail(sender,address_book, text)
    smtp.quit()

def main():
    """main function"""
    print("have admin rights=%s" % is_admin())

if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
