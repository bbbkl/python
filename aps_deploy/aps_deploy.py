# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: temp.py
#
# description
"""\n\n
    script creates zip archvie <destination> with all *.exe/*.dll files contained in given dir
"""

import re
import sys
import os.path
from argparse import ArgumentParser
from glob import glob
import zipfile
import shutil
import subprocess

VERSION = '0.1'


def get_opt_number(workdir):
    version_file = os.path.join(workdir, "_apsServerVersion", "ApsVersionDefines.h")
    #define VERSION_BUILD      241
    for line in open(version_file):
        hit = re.search(r'#define VERSION_BUILD\s+(\d+)', line)
        if hit:
            return hit.group(1)
    return "000"

def nexus_upload(src, version_id):
    file_to_upload = os.path.join(os.path.dirname(src), 'optsrv64.zip')
    shutil.copyfile(src, file_to_upload)
    cmd = [sys.executable, '-m', 'pa_nexus', 'upload', '-a', 'optsrv64', '-g', 'com.proalpha.optimizer', \
            '-v', version_id, '-f', file_to_upload, '-u', 'Jenkins.PPS', '-p', 'nexus']
    
    try:
        subprocess.call(cmd, shell=False)
    except:
        print("failed nexus upload %s / %s" % (os.path.basename(src), version_id))
    
    os.remove(file_to_upload)

def zip_files(dir_to_zip, dst, version_file=''):
    try:
        compression = zipfile.ZIP_DEFLATED
    except:
        compression = zipfile.ZIP_STORED
    zf = zipfile.ZipFile(dst, mode='w')
    try:
        extensions = ['exe', 'dll']
        for ext in extensions:
            files = glob(dir_to_zip + "/*." + ext)
            for fn in files:
                if fn.find('testrunner.exe') != -1: continue
                zf.write(fn, os.path.basename(fn), compress_type=compression)
                
        if version_file:
            zf.write(version_file, os.path.basename(version_file), compress_type=compression)
    finally:
        zf.close()

def getname_zipfile(dst_dir, pa_version, opt_num):
    name = "optsrv64.%s-%s.zip" % (pa_version.replace('.', ''), opt_num)
    return os.path.join(dst_dir, name)
    
def get_stateinfo_version(pa_version, opt_number, minor_number):
    return "%s.%s.%s" % (pa_version, opt_number, minor_number)    
    
def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('src_dir', metavar='source directory', help='src dir of optsrv64.exe and dlls')
    parser.add_argument('dst_dir', metavar='destination_zipfile', help='destination dir for created zips')
    parser.add_argument('-m', '--minor_number', metavar='string', # or stare_false
                      dest="minor_number", default='0', # negative store value
                      help="minor build number")
    parser.add_argument('-o', '--opt_number', metavar='string', # or stare_false
                      dest="opt_number", default='0', # negative store value
                      required=True, help="optimizer build number e.g. 240")
    parser.add_argument('-p', '--pa_version', metavar='string', # or stare_false
                      dest="pa_version", required=True, help="pa version e.g. 7.1")
    parser.add_argument('-zo', '--zipp_only', action='store_true',
                      dest="zip_only", help="create zip archive only")
    parser.add_argument('-av', '--add_versionfile', metavar='string', # or stare_false
                      dest="version_file", default='', help="version file")
    
    return parser.parse_args()        
        
def main():
    """main function"""
    args = parse_arguments()
    src_dir = args.src_dir
    dst_dir = args.dst_dir

    archive = getname_zipfile(dst_dir, args.pa_version, args.opt_number)
    print("creating archive %s" % archive)
    zip_files(src_dir, archive, args.version_file)
    if not args.zip_only:
        version_info = get_stateinfo_version(args.pa_version, args.opt_number, args.minor_number)
        nexus_upload(archive, version_info)
    return 0


if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
