# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: cal_check.py
#
# description
"""\n\n
    script to check for similar calendars
"""

import re
from argparse import ArgumentParser
# import os.path
# import shutil
import os


VERSION = '0.1'

class Cal():
    def __init__(self, id_val, name):
        self._id = id_val
        self._name = name
        self._elems = []

    def __str__(self):
        return "r%s name=%s #elems=%d" % (self._id, self._name, self.count())

    def get_res(self):
        return "r%s" % self._id

    def add(self, elem):
        self._elems.append(elem)

    def count(self):
        return len(self._elems)

    def get_elems(self):
        return self._elems

    def is_similar(self, other_cal):
        equal_cnt = 0
        other_elems = other_cal.get_elems()
        for idx, item in enumerate(self._elems):
            if item in other_elems:
                equal_cnt += 1
        return equal_cnt > (0.75 * len(self._elems))

class PoolRes():
    def __init__(self, id_val, name, members, prios):
        self._id = id_val
        self._name = name.replace('\t', '/')
        self._members = members
        self._prios = prios

    def __str__(self):
        equiv = {}
        for id_res in self._members:
            class_id = PoolRes.get_equivalence_class(id_res)
            equiv.setdefault(class_id, [])
            equiv[class_id].append(id_res)
        members = ""
        for idx, items in equiv.items():
            members += "  c%d#%d={%s}" % (idx, len(items), ' '.join(items))
        return "pool id={} name={:21} {}".format(self._id, self._name, members)

    @classmethod
    def set_equivalence_classes(cls, equiv_classes):
        PoolRes._equiv_classes = equiv_classes

    @classmethod
    def get_equivalence_class(cls, id_res):
        for idx, items in enumerate(PoolRes._equiv_classes):
            if id_res in items:
                return idx
        return -1

def check_calendars(filename):
    # <calendar id="c104" name="2	123" type="DisRes">
    rgx_cal = re.compile(r'<calendar\s+id="c(\d+)"\s+name="2\s+(\S+)"')
    # <calElem start="2023-02-20T07:51" end="2023-02-20T14:15" units="100" />
    rgx_cal_elem = re.compile(r'<calElem\s(start=.*units="\d+")')
    rgx_pool = re.compile(r'<altDisResSet id="([^"]*)"\s+name="([^"]*)"\s+disResIDs="([^"]*)"\s+priorities="([^"]*)"')
    calendars = []
    cal = None
    cal_elems = []
    pool_resources = []
    with open(filename, "r") as istream:
        for line in istream:
            hit = rgx_cal.search(line)
            if hit:
                id_val, name = hit.groups()
                cal = Cal(id_val, name)
            elif cal is not None:
                hit = rgx_cal_elem.search(line)
                if hit:
                    cal.add(hit.group(1))
                else:
                    calendars.append(cal)
                    cal = None
            hit = rgx_pool.search(line)
            if hit:
                id_val, name, members, prios = hit.groups()
                members = members.strip().split(' ')
                prios = prios.strip().split(' ')
                pool_resources.append(PoolRes(id_val, name, members, prios))

    if 1:
        equivalence_builder = {}

        for idx1 in range(len(calendars)):
            cal = calendars[idx1]
            handled = False
            for cal_other in equivalence_builder:
                if cal.is_similar(cal_other):
                    equivalence_builder[cal_other].append(cal)
                    handled = True
                    break
            if not handled:
                equivalence_builder[cal] = [cal]

        equivalence_classes = []
        for items in equivalence_builder.values():
            equivalence_classes.append([cal.get_res() for cal in items])

        for idx, items in enumerate(equivalence_classes):
            print("c%d -> %s" % (idx, ','.join(items)))
        print()

        PoolRes.set_equivalence_classes(equivalence_classes)

        if 0:
            for items in equivalence_builder.values():
                print("equivalent %d" % len(items))
                for item in items:
                    print(item)
                print()
                for elem in items[0].get_elems()[:10]:
                    print(elem)
                print()

        for item in pool_resources:
            print(item)

def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('inputfile', metavar='inputfile', help='input collector export file')

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
    check_calendars(args.inputfile)
    
if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
