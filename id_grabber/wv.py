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
from dateutil.relativedelta import relativedelta
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
        msg = '{:25} typ={:38}'.format(self.name(), self.get_stellentyp(False))
        msg += '--> {:35}<--'.format(self.section())
        if self.has_procura():
            msg += " prokura=1"
        if not self.is_selectable():
            msg += ' entritt=%s' % self.get_eintrittsdatum(True)
        if self.get_exit():
            msg += ' geb=%s' % self.get_birthday(True)
            msg += ' austritt=%s' % self.get_exit(True)
            msg += ' status=%s' % self.get_status()
        return msg

    def name(self):
        return self.tokens[0]

    def vorname(self):
        return self.name().split(',')[1]

    def nachname(self):
        return self.name().split(',')[0]

    def is_male(self):
        return self.tokens[self.get_idx('Geschlecht')][0] == 'M'

    def is_la(self):
        val = self.get_stellentyp()
        keys = ['Gesch�ftsf�hrungsebene',]
        for key in keys:
            if val.find(key) != -1:
                return True
        return self.has_procura()

    def get_standort(self):
        val = self.tokens[self.get_idx('Standort')]
        val = val.replace('Weilerbach (Kaiserslautern)', 'Weilerbach')
        val = val.replace('Stuttgart (B�blingen)', 'Stuttgart')
        val = val.replace('M�nchen (Ismaning)', 'M�nchen')
        return val

    def has_procura(self):
        return self.tokens[self.get_idx('Unterschriftenzusatz')] == 'ppa.'

    def pass_deadline(self, deadline='24.01.2024'):
        tp_deadline = get_datetime(deadline)
        exit = self.get_exit()
        return exit is None or exit > tp_deadline

    def pass_altersteilzeit(self):
        return not (self.is_passiv() and self.get_exit() is not None)

    def is_passiv(self):
        return self.tokens[self.get_idx('Personal Status')] == 'Passiv'

    def is_selectable(self, deadline = '24.01.2024'):
        tp_deadline = get_datetime(deadline) - relativedelta(months=6)
        return self.get_eintrittsdatum() <= tp_deadline

    def pa_what(self):
        val = self.tokens[self.get_idx('Arbeitgeber (Firmenbezeichnung)')]
        if val.find('Group')!=-1: return 'group'
        if val.find('GmbH')!=-1: return 'gmbh'
        return 'unknown'

    def get_remote_type(self):
        if self.tokens[self.get_idx('Homeoffice')].lower() in ['ja', '1']: return 'homeoffice'
        if self.tokens[self.get_idx('Remoteoffice-Erkl�rung NEU unterzeichnet')].lower() == 'ja': return 'remoteoffice'
        return "nix"

    def section(self):
        val = self.tokens[self.get_idx('Organisation max. Anteil')]
        if val.find('Team') == 0 and val.find('&') == -1: # &-check to avoid false positiv
            val = self.get_section_nth(-2) + ' ' + val
        if self.section_long().find('R&D') != -1:
            val = 'R&D ' + val
        return val

    def get_section_nth(self, nth=-1):
        tokens = self.section_long().split('>')
        return tokens[nth].strip()

    def section_long(self):
        return self.tokens[self.get_idx('Organisation > max. Anteil')]

    def get_birthday(self, raw=False):
        val = self.tokens[self.get_idx('Geburtsdatum')]
        return val if raw else get_datetime(val)

    def get_exit(self, raw=False):
        val = self.tokens[self.get_idx('Austrittsdatum')]
        return val if raw else get_datetime(val)

    def get_eintrittsdatum(self, raw=False):
        val = self.tokens[self.get_idx('Eintrittsdatum')]
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
        return self.tokens[self.get_idx('Stra�e')]

    def get_address_addon(self):
        return self.tokens[self.get_idx('Adresszusatz')]

    def get_plz(self):
        return self.tokens[self.get_idx('PLZ')]

    def get_city(self):
        return self.tokens[self.get_idx('Ort')]

    def get_status(self):
        return self.tokens[self.get_idx('Personal Status')]

    def get_comment(self):
        special = [('Finkler', '10.06.1985', 'michael.finkler.1@proalpha.com'),
                   ('Hoffmann', '31.12.1968', 'maik.hoffmann@proalpha.com'),
                   ('Hoffmann', '28.04.1996', 'maik.hoffmann.1@proalpha.com'),
                   ('Roth', '24.02.1983', 'sebastian.roth@proalpha.com'),
                   ('Roth', '28.08.1985', ' sebastian.roth.1@proalpha.com'),
                   ('Weber', '24.09.1993', 'daniel.weber@proalpha.com'),
                   ('Weber', '23.01.1987', 'daniel.weber.1@proalpha.com'), ]
        for name, birthdate, email in special:
            if(name == self.nachname() and birthdate == self.get_birthday(True)): return ' ' + email
        return ''

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

def report_passiv(items):
    print("Nachname;Vorname;M�nnlich;Stra0e;PLZ;Ort")
    for item in filter(lambda x: x.get_status() == 'Passiv', items):
        print("%s;%s;%d;%s;%s;%s" % \
              (item.nachname(), item.vorname(), 1 if item.is_male() else 0, \
               item.get_street(), item.get_plz(), item.get_city()))


def report_items(items, want_male, with_index=True):
    print('Nr.;Familienname;Vorname;Organisationseinheit')
    for idx, item in enumerate(filter(lambda x: x.is_male()==want_male, items)):
        name = item.nachname() if item.is_selectable() else item.nachname() + ' *1'
        detail = item.section() + item.get_comment()
        line = '%s;%s;%s' % (name, item.vorname(), detail)
        if with_index:
            line = '%d;%s' % (idx+1, line)
        print(line)

def report_letter_info(items):
    print('Geschlecht;Vorname;Nachname;Adresszusatz;Stra�e mit Hausnummer;PLZ;Ort')
    #items = filter(lambda x: not(x.get_standort() == 'Weilerbach' and x.get_remote_type()=='nix'), items)
    for item in items:
        line = "M" if item.is_male() else "W"
        line += ';' + item.vorname()
        line += ';' + item.nachname()
        line += ';' + item.get_address_addon()
        line += ';' + item.get_street()
        line += ';"%s"' % item.get_plz()
        line += ';' + item.get_city()
        print(line)

def report_presence_emails(items):
    msg = ''
    badies = []
    items = filter(lambda x: (x.get_standort() == 'Weilerbach' and x.get_remote_type()=='nix'), items)
    cnt = 0
    for item in items:
        prename = item.vorname().replace('Felix Benjamin', 'felixbenjamin').replace('Lisa Marie', 'lisa-marie')
        name = '%s.%s' % (prename, item.nachname())
        name = name.strip()
        name = name.lower().replace('�', 'ae').replace('�', 'oe').replace('�', 'ue').replace('�', 'ss')
        if not re.search('\s', name):
            cnt += 1
            if msg: msg += ';'
            msg += name + '@proalpha.com'
        else:
            badies.append(name)
        if cnt % 5 == 0:
            print(msg + '\n')
            msg = ''
    print(msg)
    print()
    if badies: print(badies)


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
    #items = filter(lambda x: not x.is_selectable(), items)
    #items = filter(lambda x: x.has_procura() or x.is_la(), items)
    #items = filter(lambda x: x.get_status()=='Passiv', items)
    #items = filter(lambda x: x.section().find('Team') != -1, items)
    #items = filter(lambda x: x.get_standort().find('Nashua') > -1 or x.get_standort().find('Taicang') > -1, items)

    #report_status(items)
    #report_passiv(items)
    #for item in items: print(item)
    #return 0

    with_index = True
    #report_items(items, False, with_index) # female
    report_items(items, True, with_index) # male
    #report_letter_info(items)
    #report_presence_emails(items)

    if 0:
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