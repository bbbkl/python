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
import sys
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
        self.proc_lookup = {}
        self.reserved_mat = {}
        self.items = self.parse_file(full_path_name)
        self.init_proc_lookup()

    def get_path_name(self):
        return self.path_name

    def get_items(self):
        return self.items

    def get_proc_items(self, procname):
        return self.proc_lookup[procname] if procname in self.proc_lookup else []

    def parse_file(self, filename):
        items = []
        with open(filename) as file:
            lines = [line.rstrip() for line in file]
            header = parse_header(lines[0])
            for idx, col in enumerate(header):
                self.col_lookup[col] = idx
            idx_mat = self.col_lookup['material'] if 'material' in self.col_lookup else None
            for line in lines[1:]:
                tokens = line.split(';')
                if len(tokens) > 2 and tokens[0]:
                    if idx_mat is not None:
                        tokens[idx_mat] = self.preprocess_mat(tokens[idx_mat])
                    items.append(PeggingItem(tokens, self.col_lookup))
        return items

    def preprocess_mat(self, mat):
        if len(mat) > 2 and mat[:2] == '0|':
            mat = mat[2:]
        tokens = mat.split('|')
        tokens = map(lambda x: self.truncate_reservation(x), tokens)
        tokens = filter(lambda x: x, tokens)
        return '|'.join(tokens)

    def truncate_reservation(self, val):
        if len(val) > 70:
            if not val in self.reserved_mat:
                self.reserved_mat[val] = "RESERVED_%03d" % (len(self.reserved_mat))
            return self.reserved_mat[val]
        return val

    def init_proc_lookup(self):
        for item in self.items:
            if item.is_lag() or item.is_repl_time():
                continue
            proc = item.get_proc_id()
            if proc:
                self.proc_lookup.setdefault(proc, [])
                self.proc_lookup[proc].append(item)

    def get_consumed_mat(self, procname):
        result = set()
        for item in self.get_proc_items(procname):
            if item.is_consumer():
                val = item.get_material() + '|' + str(item.get_amount())
                result.add(val)
        return result

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

    def get_idx(self, keys):
        for key in keys.split(','):
            if key in self.col_lookup:
                return self.col_lookup[key]
        print("get_idx no key (%s) in %s" % (keys, self.col_lookup.keys()))
        return None

    def get_token(self, idx):
        return self.tokens[idx] if idx < len(self.tokens) else None

    def is_delayed(self, thr_days=3):
        diff = (self.get_date() - self.get_requested_date()).days
        return diff >= thr_days

    def get_material(self, condensed_version=True):
        return self.tokens[self.get_idx('material')]

    def get_part(self):
        idx = self.get_idx('part')
        return self.tokens[idx]

    def get_prio(self):
        idx = self.get_idx('priority_scheduling,prio')
        val = self.get_token(idx)
        return int(val) if val else 0

    def get_pos(self):
        idx = self.get_idx('planning_position,pos')
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

    def is_consumer(self):
        return self.get_amount() < 0

    def get_proc_id(self):
        name = self.get_identifier()
        pos = name.find(' ')
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

def report_item(pegging, proc, items):
    earlier = filter(lambda x: x.get_duedate() > proc.get_duedate() and  (proc.get_date()-x.get_date()).days > 7, items)
    consumed_mat = pegging.get_consumed_mat(proc.get_proc_id())
    #equivalent = list(filter(lambda x: pegging.get_consumed_mat(x.get_proc_id())==consumed_mat, earlier))
    equivalent = list(earlier)
    if len(equivalent) > 0:
        print("%s xxx #=%d" % (proc, len(equivalent)))
        #print(consumed_mat)
        for item in equivalent:
            consumed_mat_item = pegging.get_consumed_mat(item.get_proc_id())
            suffix = " XXX" if consumed_mat == consumed_mat_item else ""
            print("\t%s%s" % (item, suffix))
            if not suffix:
                mat1st_only = consumed_mat - consumed_mat_item
                mat2nd_only = consumed_mat_item - consumed_mat
                print("\t%s" % ', '.join(mat1st_only))
                print("\t%s" % ', '.join(mat2nd_only))
            print()
        print()

def parse_arguments():
    """parse arguments from command line"""
    # usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('pegging_csv', metavar='pegging_csv', help='pegging csv file')
    parser.add_argument('-d', '--delay', metavar='N', type=int,  dest="threshold_delay", default=365, help="threshold delay")
    return parser.parse_args()

def main():
    """main function"""
    args = parse_arguments()

    pegging = Pegging(args.pegging_csv)
    items = filter(lambda x: x.get_part() == 'K-80' and x.get_amount() > 0 and not x.is_fixed(), pegging.get_items())
    items = sorted(items, key=lambda x: x.get_pos())
    for idx, item in enumerate(items):
        if item.is_delayed(args.threshold_delay):
            report_item(pegging, item, items[idx:])

if __name__ == "__main__":
    try:
        main()
    except BaseException:
        print('Script failed')
        raise
