# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: sample_format.py
#
# description

"""\n\n
    show usage of format
"""
from argparse import ArgumentParser
import os.path

VERSION = '0.1'


def sample_format():
    txt = "my normal braces are replaced by input ... x={} y={}".format(42, 'aha')
    print(txt)

    txt = "my you can refer with numbers to brace n ... x={1} y={0}".format(42, 'aha')
    print(txt)

    txt = "float with precision 2 f={:.2f}".format(42.12345)
    print(txt)

def parse_arguments():
    """parse arguments from command line"""
    # usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('message_file', metavar='message_file', help='input message file')
    """
    parser.add_argument('-m', '--mat-id', metavar='string', # or stare_false
                      dest="id_mat", default='', # negative store value
                      help="material id to grep")
    parser.add_argument('-c', '--count', metavar='N', type=int,
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

    sample_format()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print('Script failed')
        raise
