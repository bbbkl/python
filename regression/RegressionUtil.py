# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: RegressionUtil.py
#
# description
"""\n\n
    regression util functions
"""
import ctypes
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

def is_admin():
    """return true if we have admin rights, false otherwise"""
    try:
        is_admin = os.getuid() == 0 # non windows
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin

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
    s = smtplib.SMTP('10.1.0.62')
    s.sendmail(sender,address_book, text)
    s.quit()

def main():
    """main function"""
    print("have admin rights=%s" % is_admin())
        
if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
