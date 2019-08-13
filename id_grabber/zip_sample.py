# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: temp.py
#
# description
"""\n\n
    script creates zip archvie <destination> with all *.exe/*.dll files contained in given dir
"""

import os.path
from argparse import ArgumentParser
from glob import glob
import zipfile

VERSION = '0.1'


def zip_files(dir_to_zip, dst):
    try:
        compression = zipfile.ZIP_DEFLATED
    except:
        compression = zipfile.ZIP_STORED
    
    print('creating archive "%s"' % dst)
    zf = zipfile.ZipFile(dst, mode='w')
    try:
        extensions = ['exe', 'dll']
        for ext in extensions:
            files = glob(dir_to_zip + "/*." + ext)
            for fn in files:
                zf.write(fn, os.path.basename(fn), compress_type=compression)
    finally:
        zf.close()

    
def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('message_file', metavar='message_file', help='input message file')
    parser.add_argument('destination', metavar='destination_zipfile', help='output file')
    """
    parser.add_argument('-m', '--mat-id', metavar='string', # or stare_false
                      dest="id_mat", default='', # negative store value
                      help="material id to grep")
    parser.add_argument('-c', '--count', metavar='N', type=int, # or stare_false
                      dest="count", default=0, # negative store value
                      help="count")
    parser.add_argument('-p', '--pattern', metavar='string', # or stare_false
                      dest="pattern", default='xxx', # negative store value
                      help="search pattern within logfile")
    """
    return parser.parse_args()        
        
def main():
    """main function"""
    args = parse_arguments()
    startdir = args.message_file
    dst = args.destination
    
    zip_files(startdir, dst)



if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
