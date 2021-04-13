# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: temp.py
#
DESCRIPTION=\
"""
    script to upload given vcredist to nexus
"""

import os.path
from argparse import ArgumentParser
import sys
import subprocess

VERSION = '0.1'


def nexus_upload(src, version_id, nexus_artifact='vc_redist.x64', nexus_group='com.proalpha.3rdparty.vcredist'):
    file_to_upload = src
    cmd = [sys.executable, '-m', 'pa_nexus', 'upload', '-a', nexus_artifact, '-g', nexus_group, \
            '-v', version_id, '-f', file_to_upload, '-u', 'Jenkins.PPS', '-p', 'nexus']
    
    try:
        subprocess.call(cmd, shell=False)
    except:
        print("failed nexus upload %s / %s" % (os.path.basename(src), version_id))
    
    
    
def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('vcredist', metavar='vcredist', help='full path to vcredist')
    parser.add_argument('vcredist_version', metavar='vcredist-version', help='vcredist version')
    
    return parser.parse_args()        
        
def main():
    """main function"""
    args = parse_arguments()
    

    print("vcredist=%s" % args.vcredist)
    print("version=%s" % args.vcredist_version)
    
    nexus_upload(args.vcredist, args.vcredist_version)

    #   nexus_upload(zipfile, version_info)
    return 0


if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
