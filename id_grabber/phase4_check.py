# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: phase4_check.py
#
# description
"""\n\n
    check pegging.csv file to detect plannin problems of phase4
"""
import re
from argparse import ArgumentParser
import os.path
from glob import glob
from collections import Counter
from datetime import datetime, timedelta

VERSION = '0.1'


def get_datetime(tp_as_string):
    # format 2023-10-18
    if len(tp_as_string) == 10:
        return datetime.strptime(tp_as_string, '%Y-%m-%d')
    # format 2022-10-27 14:59:00
    return datetime.strptime(tp_as_string, '%Y-%m-%d %H:%M:%S')

def get_timestamp_key(filename):
    """return YYYYMMDD_HHMM"""
    return re.search(r'^[^_]+_(\d+_\d+)', os.path.basename(filename)).group(1)


class Pegging:
    def __init__(self, full_path_name):
        self.path_name = full_path_name
        self.col_lookup = {}
        self.items = self.parse_file(full_path_name)

    def get_path_name(self):
        return self.path_name

    def get_items(self):
        return self.items

    def parse_file(self, filename):
        items = []
        with open(filename) as file:
            lines = [line.rstrip() for line in file]
            header = parse_header(lines[0])
            for idx, col in enumerate(header):
                self.col_lookup[col] = idx
            for line in lines[1:]:
                tokens = line.split(';')
                if len(tokens) > 2 and tokens[0]:
                    items.append(PeggingItem(tokens, self.col_lookup))
        return items


class PeggingItem:
    header_items = []

    def __init__(self, values, col_lookup):
        self.tokens = values
        self.col_lookup = col_lookup

    def __str__(self):
        date = self.get_date().date()
        req_date = self.get_requested_date().date()
        prio = self.get_prio()
        id = self.get_proc_id()
        pos = self.get_pos()
        qty = self.get_amount()
        return "date=%s req_date=%s prio=%d pos=%d q=%d proc=%s" % (date, req_date, prio, pos, qty, id)

    def get_tokens(self):
        return self.tokens

    def get_idx(self, key):
        try:
            idx = self.col_lookup[key]
            # if idx >= len(self.tokens): print("idx=%d key=%s tokens=%s" % (idx, key, self.tokens))
            return idx
        except KeyError:
            #print("get_idx no such key=%s" % key)
            return None

    def get_token(self, idx):
        return self.tokens[idx] if idx < len(self.tokens) else None

    def is_delayed(self, thr_days=3):
        diff = (self.get_date() - self.get_requested_date()).days
        return diff >= thr_days

    def get_part(self):
        idx = self.get_idx('part')
        return self.tokens[idx]

    def get_prio(self):
        idx = self.get_idx('priority_scheduling')
        if idx is None:
            idx = self.get_idx('prio')
        val = self.get_token(idx)
        return int(val) if val else 0

    def get_pos(self):
        idx = self.get_idx('planning_position')
        if idx is None:
            idx = self.get_idx('pos')
        val = self.get_token(idx)
        return int(val) if val else -1

    def get_amount(self):
        idx = self.get_idx('amount')
        return int(self.tokens[idx])

    def get_identifier(self):
        idx = self.get_idx('identifier')
        return self.tokens[idx]

    def is_lag(self):
        return self.get_identifier().find('LAG') == 0

    def is_repl_time(self):
        return self.get_identifier().find('ReplenishmentTime') == 0

    def is_fixed(self):
        idx = self.get_idx('entry type')
        return 'FixedERPActivity' == self.tokens[idx]

    def is_producer(self):
        self.get_amount() > 0 and not (self.is_lag() or self.is_repl_time())

    def get_proc_id(self):
        name = self.get_identifier()
        pos = name.find(' generated act(forerun)')
        return name[:pos]

    def get_duedate(self):
        idx = self.get_idx('due_date')
        tp = self.tokens[idx]
        return get_datetime(tp)

    def get_requested_date(self):
        idx = self.get_idx('requested_date_internal')
        val = self.get_token(idx)
        return get_datetime(val) if val else None

    def get_date(self):
        idx = self.get_idx('date')
        tp = self.tokens[idx]
        return get_datetime(tp)


def parse_header(line):
    tokens = line.split(';')
    return tokens #[:-3]

def report_item(proc, items):
    earlier = list(filter(lambda x: x.get_duedate() > proc.get_duedate() and (proc.get_date()-x.get_date()).days > 7, items))
    if len(earlier) > 0:
        print("%s xxx" % proc)
        for item in earlier:
            print("\t%s" % item)
        print()

def parse_arguments():
    """parse arguments from command line"""
    # usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('pegging_csv', metavar='pegging_csv', help='pegging csv file')
    return parser.parse_args()

def main():
    """main function"""
    args = parse_arguments()

    pegging = Pegging(args.pegging_csv)
    items = filter(lambda x: x.get_part() == 'K-80' and x.get_amount() > 0 and not x.is_fixed(), pegging.get_items())
    items = sorted(items, key=lambda x: x.get_pos())
    for idx, item in enumerate(items):
        if item.is_delayed(31):
            report_item(item, items[idx:])

if __name__ == "__main__":
    try:
        main()
    except BaseException:
        print('Script failed')
        raise
