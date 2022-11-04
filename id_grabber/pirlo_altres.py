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
from datetime import datetime

VERSION = '0.1'

def get_datetime(tp_as_string):
    # format 2022-10-27 14:59:00
    return datetime.strptime(tp_as_string, '%Y-%m-%d %H:%M:%S')

class SetupRes:
    def __init__(self, full_path_name):
        self.path_name = full_path_name
        self.items = parse_file(full_path_name)
        init_tr_te(self.items)

    def get_res(self):
        name = os.path.basename(self.path_name)
        return name.split('.')[-3]

    def get_items(self):
        return self.items

class SetupItem:
    header_items = []

    def __init__(self, values):
        self.tokens = values
        self.tr_or_te = None  # 1=tr, 0=te

    def get_te(self):
        try:
            idx = SetupItem.get_index('Proc_Time')
            return int(self.tokens[idx])
        return -1

    def get_tr(self):
        try:
            idx = SetupItem.get_index('Setup_Time')
            return int(self.tokens[idx])
        return -1

    def set_is_tr(self):
        self.tr_or_te = 1
    def set_is_te(self):
        self.tr_or_te = 0
    def is_tr(self):
        if self.tr_or_te is not None:
            return self.tr_or_te
        return None

    def get_proc_id(self):
        idx = SetupItem.get_index('Activity_ID')
        tokens = self.tokens[idx].split(' ')
        return tokens[0]

    def get_process_area(self):
        idx = SetupItem.get_index('Activity_ID')
        tokens = self.tokens[idx].split(' ')
        return tokens[1]

    def get_partproc_id(self):
        idx = SetupItem.get_index('Activity_ID')
        tokens = self.tokens[idx].split(' ')
        return int(tokens[2])

    def get_act_pos(self):
        idx = SetupItem.get_index('Activity_ID')
        tokens = self.tokens[idx].split(' ')
        return int(tokens[3])

    def get_setup_type(self):
        idx = SetupItem.get_index('Sol-SetupType')
        return self.tokens[idx]

    def get_lack(self):
        idx = SetupItem.get_index('ActivityClass')
        return self.tokens[idx]

    def get_start(self):
        idx = SetupItem.get_index('Start')
        tp = self.tokens[idx]
        return get_datetime(tp)

    def get_end(self):
        idx = SetupItem.get_index('End')
        tp = self.tokens[idx]
        return get_datetime(tp)

    def get_duration(self):
        """duration in minutes"""
        duration = self.get_end() - self.get_start()
        return int(duration.total_seconds() / 60)

    @classmethod
    def set_header(cls, header_items):
        cls.header_items = header_items

    @classmethod
    def get_index(cls, key):
        return cls.header_items.index(key)

def init_tr_te(setup_items):
    if len(setup_items) == 0: return
    if len(setup_items) == 1:
        setup_items[0].set_is_te()
        return
    for idx, item in enumerate(setup_items):
        if idx == 0:
            next_item = setup_items[idx+1]
            if item.get_setup_type() == next_item.get_setup_type() and \
                item.get_partproc_id() == next_item.get_partproc_id():
                item.set_is_tr()
            else:
                item.set_is_te()
        else:
            prev_item = setup_items[idx-1]
            if item.get_setup_type() == prev_item.get_setup_type() and \
                item.get_partproc_id() == prev_item.get_partproc_id():
                item.set_is_te()
            else:
                item.set_is_tr()

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

def print_key(key, counters, tr, te):
    res = ''
    for cnt in counters:
        res += str(cnt[key]) if key in cnt else '0'
        res += '\t'
    print(res + key + " tr=%0.1f" % (tr / 1440) + "/te=%0.1f" % (te / 1440))

def pretty_print(res2counter, times):
    all = Counter()
    for cnt in res2counter.values():
        all.update(cnt)

    print('\t'.join(res2counter.keys()))
    for key, cnt in all.most_common():
        print_key(key, res2counter.values(), times[key]['tr'], times[key]['te'])

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

    alternatives = []
    for idx, fn in enumerate(args.csv_files):
        alternatives.append(SetupRes(fn))

    counters = {}
    for idx, alt in enumerate(alternatives):
        res = alt.get_res()
        items = alt.get_items()
        counters[res] = Counter(map(lambda x: x.get_lack(), items))

        if 0:
            print("res=%s #items=%d" % (res, len(items)))
            for item in items:
                print("start=%s duration=%03d setup_type=%s is_tr=%s" % (item.get_start(), item.get_duration(), item.get_lack(), item.is_tr()))
            print()

    times = {}
    for setup_res in alternatives:
        for item in setup_res.get_items():
            key = item.get_lack()
            times.setdefault(key, {'te' : 0, 'tr' : 0})
            if item.is_tr():
                times[key]['tr'] += item.get_duration()
            else:
                times[key]['te'] += item.get_duration()

    pretty_print(counters, times)



if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
