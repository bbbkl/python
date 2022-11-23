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
from glob import glob
from collections import Counter
from datetime import datetime

VERSION = '0.1'


def get_datetime(tp_as_string):
    # format 2022-10-27 14:59:00
    return datetime.strptime(tp_as_string, '%Y-%m-%d %H:%M:%S')


class Frequency:
    def __init__(self, res2counter, times):
        self.cnt_all = Counter()
        for cnt in res2counter.values():
            self.cnt_all.update(cnt)
        self.times = times

    def suffix(self, key):
        pct = self.pct_cnt(key)
        if pct > 5: return ''
        if pct > 1: return '*'
        return '**'

    def total_cnt(self):
        return sum(self.cnt_all.values())
    def total_tr(self):
        """total tr in minutes"""
        return sum(map(lambda x: self.times[x]['tr'], self.times))
    def total_te(self):
        """total te in minutes"""
        return sum(map(lambda x: self.times[x]['te'], self.times))

    def pct_cnt(self, key):
        return 100 * self.cnt_all[key] / self.total_cnt()

    def pct_tr(self, key):
        return 100 * self.times[key]['tr'] / self.total_tr()

    def pct_te(self, key):
        return 100 * self.times[key]['te'] / self.total_tr()

    def print_me(self):
        print("Frequncy cnt=%d tr=%0.1f (min) te=%0.1f (min)" % (self.total_cnt(), self.total_tr(), self.total_te()))
        for key in self.cnt_all.keys():
            cnt = self.cnt_all[key]
            cnt_pct = self.pct_cnt(key)
            tr = self.times[key]['tr'] / 60
            tr_pct = self.pct_tr(key)
            te = self.times[key]['te'] / 60
            te_pct = self.pct_te(key)
            print("%s cnt=%d (%.1f %%) tr=%.1f (%.1f %%) tr=%.1f (%.1f %%)" % (key, cnt, cnt_pct, tr, tr_pct, te, te_pct))


def get_res(csv_file):
    name = os.path.basename(csv_file)
    return name.split('.')[-3]


class SetupRes:
    def __init__(self, full_path_name):
        self.path_name = full_path_name
        self.col_lookup = {}
        self.items = self.parse_file(full_path_name)
        self.set_item_res()

    def set_item_res(self):
        res = get_res(self.get_path_name())
        for item in self.items:
            item.set_res(res)

    def get_res(self):
        return get_res(self.path_name)

    def get_path_name(self):
        return self.path_name

    def get_items(self):
        return self.items

    def mark_successor_activities(self):
        proc2idx = {}
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
        return self.get_tr() > 0 and self.get_te() == 0

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


def show_stopper(alternatives, counters, freq):
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
            if prev_item and prev_item.get_lack() == item.get_lack() and prev_item.get_tr() != item.get_tr():
                continue
            print("{:4d} {:20} {:10} {}".format(
                idx, item.get_lack() + freq.suffix(item.get_lack()), item.get_res(), item.get_fullact_info()))
            prev_item = item
        print()


def parse_header(line):
    tokens = line.split(';')
    return tokens[:-3]


def print_key(key, counters, tr, te, freq):
    res = ''
    for cnt in counters:
        res += "{:6}\t".format(cnt[key] if key in cnt else 0)
    line = '{} {:20} tr={:<5.1f} te={:<5.1f}'.format(res, key + freq.suffix(key), (tr / 60), (te / 60))
    line += '  (cnt %.1f%%, tr %.1f%%, tr %.1f%%)' % (freq.pct_cnt(key), freq.pct_tr(key), freq.pct_te(key))
    print(line)


def pretty_print(res2counter, times, freq):
    cnt_all = Counter()
    for cnt in res2counter.values():
        cnt_all.update(cnt)

    print('\t'.join(res2counter.keys()))
    for key, cnt in cnt_all.most_common():
        print_key(key, res2counter.values(), times[key]['tr'], times[key]['te'], freq)


def get_csv_files(csv_files, res_filter):
    if len(csv_files) == 1 and os.path.isdir(csv_files[0]):
        candidates = glob(csv_files[0] + "/*.csv")
        if res_filter:
            keys = res_filter.split(',')
            candidates = filter(lambda x: get_res(x) in keys, candidates)
        return candidates
    return csv_files


def make_pairs(csv_files):
    result = {}
    for item in csv_files:
        key = re.search(r'^[^_]+_(\d+)', os.path.basename(item)).group(1)
        result.setdefault(key, []).append(item)
    return result


def get_predecessors(items, idx_from, idx_to):
    proc2values = {}
    for item in items[:idx_from]:
        val = item.get_lack()
        id_proc = item.get_proc_id()
        proc2values.setdefault(id_proc, set())
        proc2values[id_proc].add(val)
    predecessors = set()
    for item in items[idx_from:idx_to+1]:
        id_proc = item.get_proc_id()
        if id_proc in proc2values:
            predecessors.update(proc2values[id_proc])
    predecessors.discard(items[idx_from].get_lack())
    return predecessors


def list_to_string(items, freq):
    res = ''
    if len(items) > 0:
        res = '('
        for item in items:
            res += item + freq.suffix(item) + ','
        res = res[:-1] + ')'
    return res


def report_group_line(items, idx_from, idx_to, freq):
    item1 = items[idx_from]
    item2 = items[idx_to]
    tp_start = item1.get_start().strftime('%d.%m. %H:%M')
    tp_end = item2.get_start().strftime('%d.%m. %H:%M')
    cnt_fixed = sum(map(lambda x: x.is_fixed(), items[idx_from:idx_to+1]))
    extra_info = '(%d fix)' % cnt_fixed if cnt_fixed > 0 else ''
    predecessors = get_predecessors(items, idx_from, idx_to)
    pred_info = list_to_string(predecessors, freq)
    val = item1.get_lack() + freq.suffix(item1.get_lack())
    print("{} - {} {:20} #{:<3} {} {}".format(
        tp_start, tp_end, val, idx_to - idx_from + 1, extra_info, pred_info))


def report_fixed_start(setup_res, stop_after_fixed, freq):
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
                report_group_line(items, idx_start, idx - 1, freq)
            idx_start = idx
            curr_value = item.get_lack()

            if stop_after_fixed and idx > 20 and not item.is_fixed():
                # pass
                break

    # report_group_line(items, idx_start, idx)
    print()

def calculate_times(alternatives):
    times = {}
    for setup_res in alternatives:
        for item in setup_res.get_items():
            key = item.get_lack()
            times.setdefault(key, {'te': 0, 'tr': 0})
            times[key]['tr'] += item.get_tr()
            times[key]['te'] += item.get_te()
    return times

def calculate_counters(alternatives):
    counters = {}
    for idx, alt in enumerate(alternatives):
        res = alt.get_res()
        items = alt.get_items()
        counters[res] = Counter(map(lambda x: x.get_lack(), items))
    return counters

def show_distribution(csv_files, short_version):
    day_files = make_pairs(csv_files)
    for day in day_files:
        alternatives = []
        for fn in day_files[day]:
            setup_res = SetupRes(fn)
            setup_res.mark_successor_activities()
            alternatives.append(setup_res)

        times = calculate_times(alternatives)
        counters = calculate_counters(alternatives)
        frequency = Frequency(counters, times)

        print(day)
        pretty_print(counters, times, frequency)
        print()
        if not short_version:
            show_stopper(alternatives, counters, frequency)
            print()

def show_sequences(csv_files, out_filter, short_version):
    alternatives = []
    for fn in csv_files:
        setup_res = SetupRes(fn)
        setup_res.mark_successor_activities()
        alternatives.append(setup_res)

    times = calculate_times(alternatives)
    counters = calculate_counters(alternatives)
    frequency = Frequency(counters, times)

    for alt in alternatives:
        if len(out_filter)==0 or alt.get_res() in out_filter:
            report_fixed_start(alt, short_version, frequency)

def get_matrix_values(tokens):
    res = set()
    property_type = tokens[4]
    if property_type == '2': # 2=assembly_part_feature
        key = 'merkmalsleiste %s/%s' % (tokens[5], tokens[6])
        res.add(tokens[7])
        res.add(tokens[16])
        return(key, res)
    if property_type == '3': # 3=bomline_part
        res.add(tokens[8])
        res.add(tokens[17])
        return('stueklistenzeile', res)
    if property_type == '4': # 4=resource
        if tokens[11] == '3': # 3=werkzeug
            res.add(tokens[13])
            res.add(tokens[21])
            return('werkzeug', res)
    if property_type == '5': # 5=operation_class
        res.add(tokens[10])
        res.add(tokens[19])
        return ('aktivitaetenklasse', res)

    print("xxx Uuups unknown property_type=%s" % property_type)
    return (None, res)

def report_matrix_values(msg_file):
    with open(msg_file) as istream:
        data = None
        matrix2values = {}
        for line in istream:
            # 2	396	DEF_ERPCommandcreate_SetupMatrixEn
            if line.find('2') == 0 and line.find('396') == 2 and data is not None:
                tokens = data.split('\t')
                matrix_id = tokens[1]
                property_type, values = get_matrix_values(tokens)
                if property_type:
                    matrix2values.setdefault(matrix_id, {})
                    matrix2values[matrix_id].setdefault(property_type, set()).update(values)
            elif line.find(r'3') == 0:
                data = line[:-1]
        for mid in matrix2values:
            print('\nmatrix=%s (%d)' % (mid, len(matrix2values[mid])))
            for property_type in matrix2values[mid]:
                print('\tproperty_type=%s' % property_type)
                for idx, val in enumerate(sorted(matrix2values[mid][property_type])):
                    print('\t\t% 3d "%s"' % (idx, val))
                print()
"""
SetupMatrixEntry 
	 1 setup_matrix_id               PC1_DRU
	 2 setup_time                    100
	 3 penalty points                0
	 4 from_property_type            5 (operation_class)
	 5 from_classification_system    
	 6 from_feature                  
	 7 from_specifictaion            
	 8 from_part                     
	 9 from_part_variant             
	10 from_activity_class           2-D-2PRHODAMINEREDC
	11 from_resource_type            0 (undefined)
	12 from_resesource               
	13 to_property_type              5 (operation_class)
	14 to_classification_system      
	15 to_feature                    
	16 to_specifictaion              
	17 to_part                       
	18 to_part_variant               
	19 to_activity_class             2-D-2PRHODAMINEREDC
	20 to_resource_type              0 (undefined)
	21 to_resource                   
"""

def report_setup_res(msg_file):
    res2matrix = {}
    with open(msg_file) as istream:
        data = None
        matrix2values = {}
        for line in istream:
            # 2	311	DEF_ERPCommandcreate_M_Ressource__
            if line.find('2') == 0 and line.find('311') == 2 and data is not None:
                tokens = data.split('\t')
                matrix_id = tokens[20]
                if matrix_id != '':
                    res_id = "%s/%s" % (tokens[1], tokens[2])
                    res2matrix[res_id] = matrix_id
            elif line.find('3') == 0:
                data = line[:-1]
    for res, matrix_id in sorted(res2matrix.items()):
        print('res=%s matrix=%s' % (res, matrix_id))

def parse_arguments():
    """parse arguments from command line"""
    # usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('csv_files', nargs='+', help='setup csv files')
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

    csv_files = get_csv_files(args.csv_files, args.res_filter)

    if args.matrix_values:
        report_setup_res(args.matrix_values)
        report_matrix_values(args.matrix_values)
        return 0

    if args.fixed_start:
        out_filter = args.output_filter.split(',') if args.output_filter else []
        show_sequences(csv_files, out_filter, args.short_version)
    else:
        show_distribution(csv_files, args.short_version)

if __name__ == "__main__":
    try:
        main()
    except BaseException:
        print('Script failed')
        raise
