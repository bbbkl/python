# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: create_reference_dir.py
#
# description
"""\n\n
    for given start directory of a compare run, create a reference dir out of the result files
"""

import sys
import os
import shutil
import datetime
from glob import glob
from argparse import ArgumentParser

VERSION = '1.0'

def filter_files(filenames, take_reference_files):
    """remove all files which belong to 'old' reference"""
    filter_out_patterns = ['TardinessReasons_Overall',]
    filter_out_patterns.append('result' if take_reference_files else 'reference')
    items = filenames
    for pattern in filter_out_patterns:
        items = [x for x in items if x.find(pattern)==-1]
    return items


def get_target_dir(current_dir, old_basedir, name_new_basedir):
    """get name of new reference directory, name_new_basedir might be just a name or a path"""
    new_basedir = name_new_basedir
    if not os.path.isdir(os.path.dirname(new_basedir)):
        base = os.path.dirname(old_basedir)
        new_basedir = os.path.join(base, name_new_basedir)
    target_dir = current_dir.replace(old_basedir, new_basedir)
    return target_dir


def take_this(filename):
    """do not copy certain files as new reference"""
    skip_keys = ['assignment.txt', 'demand_proxies.csv', 'schedInfo.csv', 'collectorexport.xml', 'report.txt', 'stdout.txt']
    for key in skip_keys:
        if filename.find(key) != -1:
            return False
    return True


def get_reference_name(filename):
    """most target filename should contain reference within their name"""
    if filename.find('pegging.csv') != -1:
        return filename.replace('pegging.csv', 'pegging.reference.csv')
    return filename.replace('result', 'reference')


def copyfiles(filenames, src_dir, dst_dir):
    """copy filenames from src_dir to dst_dir, change result to reference in names"""
    for name in filenames:
        if take_this(name):
            src = os.path.join(src_dir, name)
            dst_name = get_reference_name(name)
            dst = os.path.join(dst_dir, dst_name)
            if not os.path.isdir(os.path.dirname(dst)):
                os.makedirs(os.path.dirname(dst))
            shutil.copyfile(src, dst)

def handle_compare_dir(filenames, path, base_dir, new_refname, take_reference_files):
    """copy special files to new reference dir"""
    target_dir = get_target_dir(path, base_dir, new_refname)
    if os.path.exists(target_dir):
        print("the new reference directory '%s' may not exist before - full stop" % target_dir)
        sys.exit()
    os.makedirs(target_dir)
    files_to_copy = filter_files(filenames, take_reference_files)
    copyfiles(files_to_copy, path, target_dir)


def expand_dat_files(base_dir, dat_files):
    result = []
    for dat_file in dat_files:
        pfx = os.path.basename(dat_file)[:-4]
        for item in glob(f"{base_dir}/*/{pfx}*"):
            result.append(os.path.relpath(item, base_dir))
    return result


def create_reference(start_dir, new_refname, take_reference_files):
    """walk through directory, handle all dirs which contain a *.dat file"""
    for (path, dirs, files) in os.walk(start_dir):
        dat_files = [x for x in files if os.path.splitext(x)[1].lower()=='.dat']
        if dat_files:
            files.extend(expand_dat_files(path, dat_files))
            handle_compare_dir(files, path, start_dir, new_refname, take_reference_files)

def get_new_regression_dir(reference_dir):
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

def create_regression_dir(reference_dir):
    """for given reference dir, create regression dir with symlinks to save disk space"""
    regression_dir = get_new_regression_dir(reference_dir)
    for root, dirs, files in os.walk(reference_dir):
        dst_root = root.replace(reference_dir, regression_dir)
        for item in dirs:
            dst = os.path.join(dst_root, item)
            os.makedirs(dst)
        for item in files:
            src = os.path.join(root, item)
            dst = os.path.join(dst_root, item)
            os.symlink(src, dst)
        
def parse_arguments():
    """parse commandline arguments"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('start_dir', metavar='start_dir', help='base directory of regression run')
    parser.add_argument('new_refname', metavar='new_refname', help='directory name of new reference')
    parser.add_argument('-ref', '--take_reference', action="store_true", # or stare_false
                        dest="take_reference", default=False, # negative store value
                        help="take reference files instead of result files")
    parser.add_argument('--create_regression_dir', metavar='reference_dir',
                        dest="reference_dir", default='', # negative store value
                        help="create regression dir by copying reference dir with symlinks; add timestamp to name, return full path")
    return parser.parse_args()

def main():
    """main function"""
    args = parse_arguments()

    if args.reference_dir:
        create_regression_dir(args.reference_dir)
        print(args.reference_dir)
        return args.reference_dir

    create_reference(args.start_dir, args.new_refname, args.take_reference)


if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
