# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: split_ctp.py
#
DESCRIPTION =\
"""\n\n
    split given messagefile into separate ctp parts
"""

import os.path
from argparse import ArgumentParser
import re
from glob import glob

VERSION = '0.1'


def test_encoding(message_file):
    """check for file encoding"""
    encodings = ["UTF-8", "ISO-8859-1", "latin-1"]

    if not os.path.exists(message_file):
        raise FileNotFoundError(message_file)

    for item in encodings:
        try:
            for _ in open(message_file, encoding=item):
                pass
            return item
        except:
            pass

    raise "Cannot get right encoding, tried %s" % str(encodings)

def get_start_rgx():
    # 110 = DEF_ERPCommandCheckErpID__________
    # 250 = DEF_ERPCommandStartJobComplete____ (no contxt)
    # 111 = DEF_ERPCommandSetConfigParam______
    return re.compile(r"^(Optimizerversion:|Start\-Config|4\t1\s|2\t110|2\t250|2\t111)")

def get_start_rgx_no_dataline():
    return re.compile(r"^(Optimizerversion:|Start\-Config|4\t1\s|2\t250)")

def strip_many(dir_name):
    for item in glob(dir_name + "/*.dat"):
        strip(item)

def strip(filename):
    dst = split_ctp(filename, 1)
    if os.path.exists(dst):
        tmp_name = filename + '_tmp'
        os.rename(filename, tmp_name)
        os.rename(dst, filename)
        os.unlink(tmp_name)

def split_ctp(filename, strip_1st=0):
    """split filename into startup, ctp_001, ctp_002, ..."""
    cnt = 0
    fn_out = filename + '%03d' % cnt
    cnt += 1
    encoding_id = test_encoding(filename)
    out = open(fn_out, 'w', encoding=encoding_id)
    prev_line = None
    rgx = get_start_rgx()
    rgx_no_dataline = get_start_rgx_no_dataline()
    prev_start_idx = 0
    idx = -1
    for line in open(filename, encoding=encoding_id):
        idx += 1
        hit = rgx.search(line)
        if hit is not None:
            do_separate = idx - prev_start_idx > 20
            prev_start_idx = idx
        if do_separate:
            do_separate = False
            #print("SEPARATE idx=%d, line=%s" % (idx, line))
            if rgx_no_dataline.search(line) is not None and prev_line is not None:
                out.write("%s" % prev_line)
                prev_line = None
            if strip_1st:
                break
            out.close()
            fn_out = filename + '%03d' % cnt
            out = open(fn_out, 'w', encoding=encoding_id)
            cnt += 1
            
        if prev_line is not None:
            out.write("%s" % prev_line)
        prev_line = line
        
    if prev_line is not None:
        out.write("%s" % prev_line)
        
    out.close()
    if strip_1st:
        return fn_out

def parse_arguments():
    """parse arguments from command line"""
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('message_file', metavar='message_file', help='input message file')
    parser.add_argument('-s', '--strip', action="store_true", # or stare_false
                      dest="strip", default=False, # negative store value
                      help="strip sync/opti in place")
    parser.add_argument('-m', '--strip_many', action="store_true", # or stare_false
                      dest="strip_many", default=False, # negative store value
                      help="treat message_file as directory and strip all containted *.dat files")
    return parser.parse_args()

def main():
    """main function"""
    args = parse_arguments()
    filename = args.message_file

    if args.strip:
        strip(filename)
    elif args.strip_many:
        strip_many(filename)
    else:
        split_ctp(filename)

if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
