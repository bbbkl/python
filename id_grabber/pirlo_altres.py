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
        self.col_lookup = {}
        self.items = self.parse_file(full_path_name)
        self.set_item_res()

    def set_item_res(self):
        res = self.get_res()
        for item in self.items:
            item.set_res(res)

    def get_path_name(self):
        return self.path_name

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

    def parse_file(self, filename):
        with open(filename) as file:
            lines = [line.rstrip() for line in file]
            header = parse_header(lines[0])
            for idx, col in enumerate(header):
                self.col_lookup[col] = idx
            items = []
            for line in lines[1:]:
                if line.find('setup_spacer') != -1:
                    continue
                tokens = line.split(';')
                if len(tokens) and tokens[0]:
                    items.append(SetupItem(tokens, self.col_lookup))
            return items

class SetupItem:
    header_items = []

    def __init__(self, values, col_lookup):
        self.tokens = values
        self.col_lookup = col_lookup
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

    def get_idx(self, key):
        return self.col_lookup[key]

    def get_te(self):
        try:
            idx = self.get_idx('Proc_Time')
            return int(self.tokens[idx])
        except ValueError:
            return -1

    def get_tr(self):
        try:
            idx = self.get_idx('Setup_Time')
            return int(self.tokens[idx])
        except ValueError:
            return -1

    def is_setup_act(self):
        return self.get_tr()>0 and self.get_te() <= 0

    def get_fullact_info(self):
        idx = self.get_idx('Activity_ID')
        return self.tokens[idx]

    def get_proc_id(self):
        idx = self.get_idx('Activity_ID')
        tokens = self.tokens[idx].split(' ')
        return tokens[0]

    def get_process_area(self):
        idx = self.get_idx('Activity_ID')
        tokens = self.tokens[idx].split(' ')
        return tokens[1]

    def get_partproc_id(self):
        idx = self.get_idx('Activity_ID')
        tokens = self.tokens[idx].split(' ')
        return int(tokens[2])

    def get_act_pos(self):
        idx = self.get_idx('Activity_ID')
        tokens = self.tokens[idx].split(' ')
        return int(tokens[3])

    def get_setup_type(self):
        idx = self.get_idx('Sol-SetupType')
        return self.tokens[idx]

    def get_lack(self):
        idx = self.get_idx('ActivityClass')
        return self.tokens[idx]

    def get_start(self):
        idx = self.get_idx('Start')
        tp = self.tokens[idx]
        return get_datetime(tp)

    def get_end(self):
        idx = self.get_idx('End')
        tp = self.tokens[idx]
        return get_datetime(tp)

    def get_duration(self):
        """duration in minutes"""
        duration = self.get_end() - self.get_start()
        return int(duration.total_seconds() / 60)

    def is_fixed(self):
        idx = self.get_idx('Frozen')
        return self.tokens[idx] == '1'

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

def get_csv_files(csv_files):
    if len(csv_files)==1 and os.path.isdir(csv_files[0]):
        return glob(csv_files[0] + "/*.csv")
    return csv_files

def get_predecessors(items, idx_from, idx_to):
    proc2values = {}
    for item in items[:idx_from]:
        val = item.get_lack()
        id_proc = item.get_proc_id()
        proc2values.setdefault(id_proc, set())
        proc2values[id_proc].add(val)
    predecessors = set()
    for item in items[idx_from : idx_to+1]:
        id_proc = item.get_proc_id()
        if id_proc in proc2values:
            predecessors.update(proc2values[id_proc])
    predecessors.discard(items[idx_from].get_lack())
    return predecessors

def list_to_string(items):
    res = ''
    if len(items)>0:
        res = '('
        for item in items:
            res += item + ','
        res = res[:-1] + ')'
    return res

def report_group_line(items, idx_from, idx_to):
    item1 = items[idx_from]
    item2 = items[idx_to]
    tp_start = item1.get_start().strftime('%d.%m. %H:%M')
    tp_end = item2.get_start().strftime('%d.%m. %H:%M')
    cnt_fixed = sum(map(lambda x: x.is_fixed(), items[idx_from:idx_to+1]))
    extra_info = '(%d fix)' % cnt_fixed if cnt_fixed > 0 else ''
    predecessors = get_predecessors(items, idx_from, idx_to)
    pred_info = list_to_string(predecessors)
    print("{} - {} {:20} #{:<3} {} {}".format(tp_start, tp_end, item1.get_lack(), idx_to - idx_from + 1, extra_info, pred_info))


def report_fixed_start(setup_res, stop_after_fixed=True):
    """"report day + res and condensed sequence of fixed values"""
    headline = setup_res.get_res()
    hit = re.search(r'pirlo_2022(\d{2})(\d{2})', setup_res.get_path_name())
    if hit:
        headline += " %s.%s." % (hit.group(2), hit.group(1))
    print(headline)
    idx_start = -1
    curr_value = None
    items = setup_res.get_items()
    for idx, item in enumerate(items):
        if curr_value != item.get_lack():
            if curr_value is not None:
                report_group_line(items, idx_start, idx - 1)
            idx_start = idx
            curr_value = item.get_lack()

            if stop_after_fixed and idx > 20 and not item.is_fixed():
                #pass
                break

    #report_group_line(items, idx_start, idx)
    print()

def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('csv_files', nargs='+', help='setup csv files')
    parser.add_argument('-f', '--fixed_start', action="store_true",  # or stare_false
                        dest="fixed_start", default=False,  # negative store value
                        help="report fixed start values, start - end value #items")

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

    csv_files = get_csv_files(args.csv_files)

    alternatives = []
    for idx, fn in enumerate(csv_files):
        setup_res = SetupRes(fn)
        setup_res.mark_successor_activities()
        alternatives.append(setup_res)

    if args.fixed_start:
        for alt in alternatives:
            report_fixed_start(alt)
        return 0

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
