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
        self.set_item_res()

    def set_item_res(self):
        res = self.get_res()
        for item in self.items:
            item.set_res(res)

    def get_res(self):
        name = os.path.basename(self.path_name)
        return name.split('.')[-3]

    def get_items(self):
        return self.items

    def mark_successor_activities(self):
        proc2idx = {}
        last_found = -1
        for idx, item in enumerate(self.get_items()):
            proc_id = item.get_proc_id()
            proc2idx.setdefault(proc_id, idx)
            if idx - proc2idx[proc_id] > 1:
                prev_item = self.get_items()[proc2idx[proc_id]]
                if prev_item.get_lack() != item.get_lack():
                    item.set_stopper()
                    proc2idx[proc_id] = idx

class SetupItem:
    header_items = []

    def __init__(self, values):
        self.tokens = values
        self.stopper = False
        self.res = None

    def set_res(self, res):
        self.res = res
    def get_res(self):
        return self.res

    def set_stopper(self):
        self.stopper = True

    def is_stopper(self):
        return self.stopper

    def get_tokens(self):
        return self.tokens

    def get_te(self):
        try:
            idx = SetupItem.get_index('Proc_Time')
            return int(self.tokens[idx])
        except ValueError:
            return -1

    def get_tr(self):
        try:
            idx = SetupItem.get_index('Setup_Time')
            return int(self.tokens[idx])
        except ValueError:
            return -1

    def is_setup_act(self):
        return self.get_tr()>0 and self.get_te() <= 0

    def get_fullact_info(self):
        idx = SetupItem.get_index('Activity_ID')
        return self.tokens[idx]

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

def is_multi_res_stopper(stopper_items):
    res = None
    for _, item in stopper_items:
        if res is None:
            res = item.get_res()
        if res != item.get_res():
            return True
    return False
def show_stopper(alternatives, counters):
    items = []
    for alt in alternatives:
        items.extend(alt.get_items())

    cnt_all = Counter()
    for counter in counters.values():
        cnt_all.update(counter)

    proc2items = {}
    stopper_ids = []
    for idx, item in enumerate(items):
        proc_id = item.get_proc_id()
        proc2items.setdefault(proc_id, [])
        proc2items[proc_id].append((idx, item))
        if item.is_stopper() and proc_id not in stopper_ids:
            stopper_ids.append(proc_id)
    for proc_id in stopper_ids:
        # if not is_multi_res_stopper(proc2items[proc_id]): continue
        prev_item = None
        tuples = proc2items[proc_id]
        tuples.sort(key=lambda x: x[1].get_start())
        for idx, item in tuples:
            if prev_item and prev_item.get_lack() == item.get_lack() and prev_item.get_tr()!=item.get_tr():
                continue
            cnt = cnt_all[item.get_lack()]
            print("{:4d} {:20} cnt={:<4d} {:10} {}".format(idx, item.get_lack(), cnt, item.get_res(), item.get_fullact_info()))
            prev_item = item
        print()

def parse_file(filename):
    with open(filename) as file:
        lines = [line.rstrip() for line in file]
        header = parse_header(lines[0])
        SetupItem.set_header(header)
        items = []
        for line in lines[1:]:
            if line.find('setup_spacer') != -1:
                continue
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
        res += "{:6}\t".format(cnt[key] if key in cnt else 0)
    print('{} {:20} tr={:<5.1f} te={:<5.1f}'.format(res, key, (tr / 60), (te / 60) ))

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
        setup_res = SetupRes(fn)
        setup_res.mark_successor_activities()
        alternatives.append(setup_res)

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
            times[key]['tr'] += item.get_tr()
            times[key]['te'] += item.get_te()

    pretty_print(counters, times)
    print()
    show_stopper(alternatives, counters)




if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
