# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: pirlo_altres.py
#
# description
"""\n\n
    script to try something out and which is not lost after shutdown
"""
import re
from argparse import ArgumentParser
import os.path
import shutil
from subprocess import run, PIPE
from glob import glob
from collections import Counter

VERSION = '0.1'

def get_res(full_path_name):
    name = os.path.basename(full_path_name)
    return name.split('.')[-3]

class SetupItem:
    header_items = []

    def __init__(self, values):
        self.tokens = values

    def get_lack(self):
        idx = SetupItem.get_index('ActivityClass')
        return self.tokens[idx]

    @classmethod
    def set_header(cls, header_items):
        cls.header_items = header_items

    @classmethod
    def get_index(cls, key):
        return cls.header_items.index(key)

def parse_file(filename):
    with open(filename) as file:
        lines = [line.rstrip() for line in file]
        header = parse_header(lines[0])
        SetupItem.set_header(header)
        items = []
        for line in lines[1:]:
            tokens = line.split(';')
            if len(tokens) and tokens[0]:
                items.append(SetupItem(tokens))
        return items

def parse_header(line):
    tokens = line.split(';')
    return tokens[:-3]

def print_key(key, counters):
    res = ''
    for cnt in counters:
        res += str(cnt[key]) if key in cnt else '0'
        res += '\t'
    print(res + key)

def pretty_print(res2counter):
    all = Counter()
    for cnt in res2counter.values():
        all.update(cnt)

    print('\t'.join(res2counter.keys()))
    for key, cnt in all.most_common():
        print_key(key, res2counter.values())

def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('csv_files', nargs='+', help='setup csv files')

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

    counters = {}
    for idx, fn in enumerate(args.csv_files):
        res = get_res(fn)
        items = parse_file(fn)
        counters[res] = Counter(map(lambda x: x.get_lack(), items))

    pretty_print(counters)



if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
