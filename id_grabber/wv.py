# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: wv.py
#
# description
"""\n\n
    get wv items
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
        return datetime.strptime(tp_as_string, '%d.%m.%Y')
    return None
class MAL:
    def __init__(self, full_path_name):
        self.path_name = full_path_name
        self.col_lookup = {}
        self.items = self.parse_file(full_path_name)

    def get_items(self):
        return self.items

    def get_path_name(self):
        return self.path_name

    def parse_file(self, filename):
        items = []
        with open(filename, encoding="utf-8") as file:
            lines = [line.rstrip() for line in file]
            header = parse_header(lines[0])
            for idx, col in enumerate(header):
                self.col_lookup[col] = idx
            for line in lines[1:]:
                tokens = line.split(';')
                if len(tokens) > 2:
                    items.append(MA(tokens, self.col_lookup))
        return items

class MA:
    header_items = []

    def __init__(self, values, col_lookup):
        self.tokens = values
        self.col_lookup = col_lookup

    def __str__(self):
        return "%s typ='%s'" % (self.name(), self.get_stellentyp())

    def name(self):
        return self.tokens[0]

    def is_male(self):
        return self.tokens[self.get_idx('Geschlecht')][0] == 'M'

    def is_la(self):
        val = self.get_stellentyp()
        if val.find('kein SMT') != -1:
            return False
        keys = ['- SMT', 'Geschäftsführungsebene']
        for key in keys:
            if val.find(key) != -1:
                return True
        return False

    def has_procura(self):
        return self.tokens[self.get_idx('Unterschriftenzusatz')] == 'ppa.'

    def pass_deadline(self, deadline="17.01.2024"):
        tp_deadline = get_datetime(deadline)
        exit = self.get_exit()
        return exit is None or exit > tp_deadline

    def pass_altersteilzeit(self, deadline="01.01.1966"):
        tp_deadline = get_datetime(deadline)
        return not(self.is_passiv() and self.birthday() < tp_deadline)

    def is_passiv(self):
        return self.tokens[self.get_idx('Personal Status')] == 'Passiv'

    def birthday(self):
        return get_datetime(self.tokens[self.get_idx('Geburtsdatum')])

    def get_exit(self):
        val = self.tokens[self.get_idx('Austrittsdatum')]
        return get_datetime(val)

    def get_stellentyp(self):
        return self.tokens[self.get_idx('Stellentyp')]

    def get_tokens(self):
        return self.tokens

    def get_idx(self, keys):
        for key in keys.split(';'):
            if key in self.col_lookup:
                return self.col_lookup[key]
        print("get_idx no key (%s) in %s" % (keys, self.col_lookup.keys()))
        return None

    def get_token(self, idx):
        return self.tokens[idx] if idx < len(self.tokens) else None

def parse_header(line):
    tokens = line.split(';')
    return tokens

def parse_arguments():
    """parse arguments from command line"""
    # usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('br_csv', metavar='br_csv', help='br csv file')

    return parser.parse_args()


def main():
    """main function"""
    args = parse_arguments()

    mal = MAL(args.br_csv)
    items = mal.get_items()
    #items = filter(lambda x: not x.is_la(), items)
    #items = filter(lambda x: x.pass_deadline(), items)
    #items = filter(lambda x: not x.pass_altersteilzeit(), items)
    items = filter(lambda x: x.has_procura(), items)

    for item in items: print(item)

    if 0:
        cnt_total = cnt_male = 0
        for item in items:
            cnt_total += 1
            if item.is_male():
                cnt_male += 1
        print("total=%d #m=%d (%.1f)" % (cnt_total, cnt_male, 100*cnt_male/cnt_total))


if __name__ == "__main__":
    try:
        main()
    except BaseException:
        print('Script failed')
        raise