# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: datfile_rename.py
#
# description
from pathlib import Path
"""\n\n
    rename given dat files and directories
"""

import sys
import re
import os.path
from argparse import ArgumentParser

VERSION = '0.1'

def truncate(name):
    hit = re.search(('(testrunner_tst_)'), name)
    if not hit:
        hit = re.search(r"([_0-9]+)_ctp", name)
    if not hit:
        hit = re.search(r"([_0-9]+[0-9])(.dat|_reference.csv|_headproc_reference.csv)", name)
    if hit:
        return name.replace(hit.group(1), '')
    return name

def rename_files_in_dir(path, old, new):
    """rename contained files in directory"""
    key_old = old[:-4]
    key_new = new[:-4]
    files = os.listdir(path)
    with_unfix = old.find('_unfix') != -1
    for fn in files:
        if re.search(r'^\d{3}_', fn): continue
        if not with_unfix and fn.find('_unfix') != -1: continue
        if fn.find(key_old) != -1:
            fn_old = os.path.join(path, fn)
            new_name = fn.replace(key_old, key_new)
            fn_new = os.path.join(path, new_name)
            print("\t\t%s -> %s" % (fn_old, fn_new))
            os.rename(fn_old, fn_new)

def get_new_name(idx, old):
    """rename bornemann_20130925.dat to idx_bornemann.dat"""
    new = old.replace('.dat', '')
    hit = re.search(r"([a-zA-Z].*[a-zA-Z])", new)
    new = hit.group(1)
    return "%03d_%s.dat" % (idx, new)

def rename_datfiles(idx, dat_files, path):
    if not dat_files: return
    fn = dat_files[0]
    print("%d\t%s -> %s" % (idx, fn, get_new_name(idx, fn)))
    rename_files_in_dir(path, fn, get_new_name(idx, fn))
    if len(dat_files) > 1:
        for i, fn in enumerate(dat_files[1:]):
            new_idx = idx + i + 1
            print("\t%d\t%s -> %s" % (new_idx, fn, get_new_name(new_idx, fn)))
            rename_files_in_dir(path, fn, get_new_name(new_idx, fn))
            
def rename_msg_dir(idx, path):
    old_name = path
    dirname = os.path.basename(path)
    new_name = os.path.join(os.path.dirname(path), "%03d_%s" % (idx, dirname))
    print("xxx %s -> %s" % (old_name, new_name))
    os.rename(old_name, new_name)            
            
def get_message_files(start_dir):
    """walk through directory, handle all dirs which contain a *.dat file"""
    result = []
    idx = 1
    for (path, dirs, files) in os.walk(start_dir):
        dat_files = [x for x in files if os.path.splitext(x)[1].lower()=='.dat']
        if dat_files:
            rename_datfiles(idx, dat_files, path)
            result.extend(dat_files)
            rename_msg_dir(idx, path)
        idx += len(dat_files) 
    return result

def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)

    parser.add_argument('message_dir', metavar='message_dir', help='root dir of message files')
    """
    parser.add_argument('-rid', '--res_id', metavar='string',
                      dest="res_id", default='',
                      help="grep process ids of processes which require given resource id")
    parser.add_argument('--fixed_ids', action="store_true", # or store_false
                      dest="fixed_ids", default=False, # negative store value
                      help="grep ids of completely fixed processes out of message_file")
    parser.add_argument('--partproc_duedate', action="store_true", # or store false)
                        dest='partproc_duedate', default=False, 
                        help="grep ids of processes which contain a partproc with own duedate")
    """

    return parser.parse_args()

def main():
    """main function"""
    args = parse_arguments()
    dirname = args.message_dir

    message_files = get_message_files(dirname)

if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
