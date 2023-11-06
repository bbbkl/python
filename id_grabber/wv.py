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
from collections import Counter

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


def get_datetime(tp_as_string):
    # format 2023-10-18
    if len(tp_as_string) == 10:
        return datetime.strptime(tp_as_string, '%d.%m.%Y')
    return None

def find_ambigeous(items):
    handled = set()
    for item in items:
        name = item.name()
        if name in handled:
            print('ambigeous %s' % name)
        handled.add(name)
    print()

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
        enc = test_encoding(filename)
        with open(filename, encoding=enc) as file:
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
        msg = '{:25} typ={:36}'.format(self.name(), self.get_stellentyp(False))
        if self.has_procura():
            msg += " prokura=1"
        if self.get_exit():
            msg += ' geb=%s' % self.get_birthday(True)
            msg += ' austritt=%s' % self.get_exit(True)
            msg += ' status=%s' % self.get_status()
        return msg

    def name(self):
        return self.tokens[0]

    def is_male(self):
        return self.tokens[self.get_idx('Geschlecht')][0] == 'M'

    def is_la(self):
        val = self.get_stellentyp()
        keys = ['Geschäftsführungsebene',]
        for key in keys:
            if val.find(key) != -1:
                return True
        return self.has_procura()

    def get_standort(self):
        val = self.tokens[self.get_idx('Standort')]
        val = val.replace('Weilerbach (Kaiserslautern)', 'Weilerbach')
        val = val.replace('Stuttgart (Böblingen)', 'Stuttgart')
        val = val.replace('München (Ismaning)', 'München')
        return val

    def has_procura(self):
        return self.tokens[self.get_idx('Unterschriftenzusatz')] == 'ppa.'

    def pass_deadline(self, deadline="24.01.2024"):
        tp_deadline = get_datetime(deadline)
        exit = self.get_exit()
        return exit is None or exit > tp_deadline

    def pass_altersteilzeit(self):
        return not (self.is_passiv() and self.get_exit() is not None)

    def is_passiv(self):
        return self.tokens[self.get_idx('Personal Status')] == 'Passiv'

    def pa_what(self):
        val = self.tokens[self.get_idx('Arbeitgeber (Firmenbezeichnung)')]
        if val.find('Group')!=-1: return 'group'
        if val.find('GmbH')!=-1: return 'gmbh'
        return 'unknown'

    def get_remote_type(self):
        if self.tokens[self.get_idx('Homeoffice')].lower() == 'ja': return 'homeoffice'
        if self.tokens[self.get_idx('Remoteoffice-Erklärung NEU unterzeichnet')].lower() == 'ja': return 'remoteoffice'
        return "nix"

    def section(self):
        return self.tokens[self.get_idx('Organisation max. Anteil')]

    def get_birthday(self, raw=False):
        val = self.tokens[self.get_idx('Geburtsdatum')]
        return val if raw else get_datetime(val)

    def get_exit(self, raw=False):
        val = self.tokens[self.get_idx('Austrittsdatum')]
        return val if raw else get_datetime(val)

    def get_stellentyp(self, long_version=True):
        val = self.tokens[self.get_idx('Stellentyp')]
        if long_version:
            return val
        pos = val.find(',')
        if pos > 0:
            return val[0:pos]
        return val

    def get_street(self):
        return self.tokens[self.get_idx('Straße')]

    def get_address_addon(self):
        return self.tokens[self.get_idx('Adresszusatz')]

    def get_plz(self):
        return self.tokens[self.get_idx('PLZ')]

    def get_city(self):
        return self.tokens[self.get_idx('Ort')]

    def get_status(self):
        return self.tokens[self.get_idx('Personal Status')]

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

def report_office_type(items, standort='Weilerbach'):
    items = filter(lambda x: x.get_standort()==standort, items)
    office_types = Counter(x.get_remote_type() for x in items)
    print("Standort %s" % standort)
    for kind in office_types.most_common():
        print("  %s: %d" % (kind[0], kind[1]))

def report_all_names(items):
    names = [x.name() for x in items]
    names.sort(key=lambda s: s.lower())
    for name in names:
        print(name)

def report_standorte(items):
    standorte = Counter([x.get_standort() for x in items])
    for standort in standorte.most_common():
        print("%s: %d" % (standort[0], standort[1]))

def report_status(items):
    status = Counter([x.get_status() for x in items])
    for item in status.most_common():
        print('%s: %d' % (item[0], item[1]))

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

    if 0:
        find_ambigeous(items)
        report_office_type(items)
        #report_standorte(items)
        return 0

    if 0: # report all name
        report_all_names(items)
        return 0;

    items = filter(lambda x: not x.is_la(), items)
    items = filter(lambda x: x.pass_deadline(), items)
    items = filter(lambda x: x.pass_altersteilzeit(), items)
    #items = filter(lambda x: x.has_procura() or x.is_la(), items)
    #items = filter(lambda x: x.get_status()=='Passiv', items)

    #report_status(items)
    #for item in items: print(item)
    #return 0

    if 1:
        cnt_total = cnt_male = 0
        for item in items:
            cnt_total += 1
            if item.is_male():
                cnt_male += 1
        cnt_female = cnt_total - cnt_male
        print("total=%d #m=%d (%.1f) #f=%d (%.1f)" %
              (cnt_total,
               cnt_male, 100*cnt_male/cnt_total,
               cnt_female, 100*cnt_female/cnt_total))


if __name__ == "__main__":
    try:
        main()
    except BaseException:
        print('Script failed')
        raise