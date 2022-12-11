# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: pegging.py
#
# description
"""\n\n
    script to check pegging.csv content
"""
import re
from argparse import ArgumentParser
import os.path
from glob import glob
from collections import Counter
from datetime import datetime

VERSION = '0.1'


def get_datetime(tp_as_string):
    # format 2022-10-27 14:59:00
    try:
        return datetime.strptime(tp_as_string, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return None

def dt2str(dt_obj, date_only=True):
    if dt_obj is None:
        return 10 * ' ' if date_only else 16 * ' '
    if date_only:
        return dt_obj.strftime('%Y-%m-%d')
    return dt_obj.strftime('%Y-%m-%d %H:%M')

class Pegging:
    def __init__(self, csv_file):
        self.file = csv_file
        self.header = []
        self.col_lookup = {}
        self.items = []
        self.parse_file(csv_file)

    def parse_file(self, filename):
        with open(filename) as file:
            lines = [line.rstrip() for line in file]
            self.header = lines[0].split(';')
            for idx, col in enumerate(self.header):
                self.col_lookup[col] = idx
            self.items = []
            for line in lines[1:]:
                tokens = line.split(';')
                if len(tokens) and tokens[0]:
                    self.items.append(PeggingItem(tokens, self.col_lookup))

    def report(self, part):
        items = filter(lambda x: x.get_part() == part, self.items)
        sum = 0
        print("part=%s" % part)
        print('{:>8}   {:>6}   {:>10}   {:>10}   {:>5}   {:20}'.format('sum', 'amount', 'date', 'dd', 'pos', 'id'))
        for item in items:
            amount, id, date, dd, pos = item.get_amount(), item.get_id(), item.get_date(), item.get_due_date(), item.get_pos()
            sum += amount
            print('{:8d}   {:6}   {:10}   {:>10}   {:>5}   {:20}'.format(
                sum, amount, dt2str(date), dt2str(dd), pos, id))

    def print_me(self):
        print("pegging csv")

class PeggingItem:
    def __init__(self, values, col_lookup):
        self.tokens = values
        self.col_lookup = col_lookup
        self.stopper = False
        self.res = None

    def get_token(self, key):
        idx = self.col_lookup[key]
        if len(self.tokens) <= idx:
            return ''
        return self.tokens[idx]

    def get_material(self):
        return self.get_token('material')

    def get_part(self):
        return self.get_token('part')

    def get_date(self):
        val = self.get_token('date')
        return get_datetime(val)

    def get_mrp_date(self):
        val = self.get_token('date_mrp')
        return get_datetime(val)

    def get_due_date(self):
        val = self.get_token('due_date')
        return get_datetime(val)

    def get_requested_date(self):
        val = self.get_token('requested_date_internal')
        return get_datetime(val)

    def get_id(self):
        return self.get_token('identifier')

    def get_type(self):
        return self.get_token('entry type')

    def get_pos(self):
        return self.get_token('planning_position')

    def get_age(self):
        return self.get_token('age')

    def get_dpl(self):
        return self.get_token('dispo_level')

    def get_prio(self):
        return self.get_token('priority_scheduling')

    def get_amount(self):
        return 0 if self.is_rlt() else int(self.get_token('amount'))

    def is_rlt(self):
        return self.get_type() == 'ReplenishmentTime'

    def is_stock(self):
        return self.get_id() == 'LAG'

    def get_tokens(self):
        return self.tokens

def parse_arguments():
    """parse arguments from command line"""
    # usage = "usage: %(prog)s [options] <pgegging.csv>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('pegging_csv', metavar='pegging_csv', help='input pegging.csv')
    parser.add_argument('-p', '--part', metavar='string',
                        dest="part", default='',
                        help="report pegging of given part")
    """
    parser.add_argument('-r', '--res_filter', metavar='string',
                        dest="res_filter", default='',
                        help="filter given resources, expect main input to be a directory")
    parser.add_argument('-o', '--output_filter', metavar='string',
                        dest="output_filter", default='',
                        help="if non-empty, filter given resources in output")
    parser.add_argument('-f', '--fixed_start', action="store_true",  # or stare_false
                        dest="fixed_start", default=False,  # negative store value
                        help="report fixed start values, start - end value #items")
    parser.add_argument('-s', '--short_version', action="store_true",  # or stare_false
                        dest="short_version", default=False,  # negative store value
                        help="report short version of fixed start values, start - end value #items")
    parser.add_argument('-m', '--maxtrix_values', metavar='string',
                        dest="matrix_values", default='',
                        help="report setup matrix values for given messagefile")
   
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

    pegging_csv = args.pegging_csv

    pegging = Pegging(pegging_csv)
    if args.part:
        pegging.report(args.part)

if __name__ == "__main__":
    try:
        main()
    except BaseException:
        print('Script failed')
        raise
