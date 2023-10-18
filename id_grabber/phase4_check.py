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
from collections import Counter
from glob import glob

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
        self.now = None

    def get_now(self):
        """now is date of any LAG item, all should be equal"""
        if self.now is None:
            for item in self.items:
                if item.get_identifier().strip() == "LAG":
                    self.now = item.get_date()
                    break
        return self.now

    def get_diff2now(self, dt):
        return max(0, (self.get_now() - dt).days)

    def get_path_name(self):
        return self.path_name

    def get_items(self):
        return self.items

    def get_dpl_items(self, dpl):
        return filter(lambda x: x.get_dpl()==dpl and x.is_producer(), self.items)

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
        what = self.get_identifier()
        amount = self.get_amount()
        date = self.get_date().date()
        req_date = self.get_requested_date().date() if self.get_requested_date() else None
        prio = self.get_prio()
        id = self.get_proc_id()
        pos = self.get_pos()
        qty = self.get_amount()
        return "what=%s amount=%s date=%s req_date=%s prio=%.1f pos=%d q=%d proc=%s" % (what, amount,
                                                                                        date, req_date, prio, pos, qty, id)

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

    def get_demand_topmost(self):
        idx = self.get_idx('demand_topmost')
        return self.tokens[idx] if idx < len(self.tokens) else None

    def is_delayed(self, thr_days=3):
        return self.get_delay() >= thr_days

    def get_delay(self):
        diff = (self.get_date() - self.get_due_date()).days
        return diff

    def get_material(self):
        return self.tokens[self.get_idx('material')]

    def get_dpl(self):
        idx = self.get_idx('dispo_level,dpl')
        return int(self.tokens[idx]) if idx < len(self.tokens) else None

    def get_part(self):
        return self.tokens[self.get_idx('part')]

    def get_prio(self):
        val = self.get_token(self.get_idx('priority_scheduling,prio'))
        return float(val) if val else 0

    def get_pos(self):
        val = self.get_token(self.get_idx('planning_position,pos'))
        return int(val) if val else -1

    def get_amount(self):
        return int(self.tokens[self.get_idx('amount')])

    def get_identifier(self):
        idx = self.get_idx('identifier')
        return self.tokens[idx] if idx < len(self.tokens) else None

    def is_lag(self):
        return self.get_identifier().find('LAG') == 0

    def is_repl_time(self):
        return self.get_identifier().find('ReplenishmentTime') == 0

    def is_fixed(self):
        return 'FixedERPActivity' == self.tokens[self.get_idx('entry type')]

    def is_producer(self):
        return self.get_amount() > 0 and not (self.is_lag() or self.is_repl_time())

    def is_consumer(self):
        return self.get_amount() < 0

    def is_started(self):
        val = self.get_token(self.get_idx('is_started'))
        return val == '1'

    def get_proc_id(self):
        name = self.get_identifier()
        pos = name.find(' ')
        return name[:pos]

    def get_duedate(self):
        tp = self.tokens[self.get_idx('due_date')]
        return get_datetime(tp)

    def get_requested_date(self):
        tp = self.get_token(self.get_idx('requested_date_internal'))
        return get_datetime(tp) if tp else None

    def get_due_date(self):
        tp = self.get_token(self.get_idx('due_date'))
        return get_datetime(tp) if tp else None

    def get_date(self):
        tp = self.tokens[self.get_idx('date')]
        return get_datetime(tp)


def parse_header(line):
    tokens = line.split(';')
    return tokens #[:-3]

def report_item(pegging, proc, items, dominate_material):
    earlier = filter(lambda x: x.get_duedate() > proc.get_duedate() and  (proc.get_date()-x.get_date()).days > 7, items)
    consumed_mat = pegging.get_consumed_mat(proc.get_proc_id())
    if dominate_material:
        earlier = list(filter(lambda x: pegging.get_consumed_mat(x.get_proc_id())>=consumed_mat, earlier))
    equivalent = list(earlier)
    if len(equivalent) > 0:
        print("%s xxx #=%d" % (proc, len(equivalent)))
        #print(consumed_mat)
        for item in equivalent:
            consumed_mat_item = pegging.get_consumed_mat(item.get_proc_id())
            suffix = " XXX" if consumed_mat <= consumed_mat_item else ""
            print("\t%s%s" % (item, suffix))
            if consumed_mat != consumed_mat_item:
                mat1st_only = consumed_mat - consumed_mat_item
                mat2nd_only = consumed_mat_item - consumed_mat
                print("\tref_only=%s" % ', '.join(mat1st_only))
                print("\tcmp_only=%s" % ', '.join(mat2nd_only))
            print()
        print()

def detect_problems_material(pegging, material, threshold_delay, require_same_material=False):
    items = filter(lambda x: not(x.is_lag() or x.is_repl_time() or x.is_fixed()), pegging.get_items())
    items = filter(lambda x: x.get_part() == material and x.get_amount() > 0, items)
    items = sorted(items, key=lambda x: x.get_pos())
    for idx, item in enumerate(items):
        if item.is_delayed(threshold_delay):
            report_item(pegging, item, items[idx:], require_same_material)

def report_one_proc(pegging, process):
    proc_item = None
    for item in pegging.get_proc_items(process):
        if item.is_producer():
            proc_item = item
            break
    if proc_item:
        items = filter(lambda x: not (x.is_lag() or x.is_repl_time() or x.is_fixed()), pegging.get_items())
        items = filter(lambda x: x.get_part() == proc_item.get_part() and x.get_amount() > 0, items)
        items = sorted(items, key=lambda x: x.get_pos())
        idx = items.index(proc_item)
        report_item(pegging, proc_item, items[idx:], False)

def get_material_to_check(pegging, mat_filter, dpl=0):
    material_to_check = set()
    if mat_filter:
        for mat in mat_filter.split(','):
            material_to_check.add(mat)
    else:
        for item in pegging.get_dpl_items(dpl):
            if item.get_part() not in material_to_check:
                material_to_check.add(item.get_part())
    return material_to_check

def detect_problems(pegging, threshold_delay, require_same_material, material_to_check):
    for material in sorted(material_to_check):
        print("%s %s %s" % (5*'#', material, 15*'#'))
        detect_problems_material(pegging, material, threshold_delay, require_same_material)

def show_process_info(pegging, processes):
    procs = filter(lambda x: x.get_proc_id() in processes and x.is_producer(), pegging.get_items())
    ref_mat = None
    for proc in procs:
        if ref_mat is None:
            ref_mat = pegging.get_consumed_mat(proc.get_proc_id())
        print(proc)
        print("produces=%s" % proc.get_material())
        proc_mat = pegging.get_consumed_mat(proc.get_proc_id())
        if ref_mat != proc_mat:
            print("ref_proc mat only=%s" % ', '.join(ref_mat - proc_mat))
            print("cmp_proc mat only=%s" % ', '.join(proc_mat - ref_mat))
        print()

def report_tardiness(pegging, with_details):
    if 0:
        items = filter(lambda x: x.is_producer() and x.get_demand_topmost() and len(x.get_demand_topmost())>5 and len(x.get_demand_topmost())<40 and x.get_identifier().find(x.get_demand_topmost()[4:]) != -1, pegging.get_items())
        for item in items:
            print("part=%s id=%s" % (item.get_part(), item.get_identifier()))
        return
    items = filter(lambda x: x.get_demand_topmost() and x.get_identifier().find(x.get_demand_topmost()) != -1, pegging.get_items())
    #items = filter(lambda x: x.get_identifier().find('DemandProxy_SafetyStock') == -1, items)
    if 0:
        for item in items:
            dp = pegging.get_diff2now(item.get_due_date())
            print("'%s' dd=%s dp=%d is_delayed=%s" % (item.get_identifier(), item.get_due_date(), dp, item.is_delayed(1)))
        return
    cnt = 0
    cnt_delayed = 0
    cnt_in_time = 0
    tardiness_days = 0
    counter = Counter()
    bin_counter = Counter()
    past_days = 0
    for item in items:
        counter[item.get_delay()] += 1
        bin_counter[round(item.get_delay() / 1)] += 1
        cnt += 1
        if item.is_delayed(1):
            cnt_delayed += 1
            tardiness_days += item.get_delay()
            past_days += pegging.get_diff2now(item.get_due_date())
        else:
            cnt_in_time += 1
    print("#cluster_heads=%d #in_time=%d #delayed=%d #days_delay=%d #past_days=%d avg_delay=%0.1f avg_delay_no_past=%0.1f" % \
          (cnt, cnt_in_time, cnt_delayed, tardiness_days, past_days, tardiness_days / cnt, (tardiness_days - past_days) / cnt))
    #for diff in sorted(counter.keys()): print("%d: %d" % (diff, counter[diff]))

    if with_details:
        accu = 0
        for diff in sorted(bin_counter.keys()):
            accu += bin_counter[diff]
            print("{:3} {:4} {}".format(diff, bin_counter[diff], accu))
    print()

def check_assignment_errors(pegging):
    mat2Items = {}
    for item in pegging.get_items():
        mat = item.get_material()
        mat2Items.setdefault(mat, [])
        mat2Items[mat].append(item)
    mat = '11200616-0353197'
    print("%s -> %s" % (mat, mat2Items[mat][-1]))
def get_pegging_csf_files(pegging_path):
    if os.path.isfile(pegging_path):
        return [pegging_path,]
    return glob(pegging_path + "/*.pegging*.csv")

def get_material_curve_quality(items):
    bad_cnt = 0
    started_cnt = 0
    prev_is_started = True
    for item in items:
        if item.is_started() != prev_is_started and not prev_is_started:
            bad_cnt += 1
        prev_is_started = item.is_started()
    return bad_cnt * 100 / len(items), bad_cnt, len(items)

def get_materials(mat_as_str):
    result = []
    for mat in mat_as_str.split(','):
        mat = mat.strip()
        if mat:
            result.append(mat)
    return result

def check_is_started_quality(pegging, materials):
    items = filter(lambda x: x.is_producer(), pegging.get_items())
    if materials:
        items = filter(lambda x: x.get_material() in materials, items)
    mat2Items = {}
    for item in items:
        mat = item.get_material()
        mat2Items.setdefault(mat, [])
        mat2Items[mat].append(item)
    for mat in mat2Items:
        quality, cnt_bad, cnt_total = get_material_curve_quality(mat2Items[mat])
        if quality > 0 or cnt_total > 1:
            cnt_started = sum(1 for item in mat2Items[mat] if item.is_started())
            print("%s %0.1f (%d/%d/%d)" % (mat, quality, cnt_bad, cnt_started, cnt_total))

def parse_arguments():
    """parse arguments from command line"""
    # usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('pegging_csv', metavar='pegging_csv', help='pegging csv file')
    parser.add_argument('-d', '--delay', metavar='N', type=int,  dest="threshold_delay", default=365, help="threshold delay")
    parser.add_argument('-dm', '--dominate_material', action="store_true", dest="dominate_mat", default=False, help="dominate material filter")
    parser.add_argument('-f', '--filter', metavar='N', type=str, dest="mat_filter", default="", help="material filter")
    parser.add_argument('-pi', '--process_info', metavar='N', type=str, dest="process_info", default="", help="process info")
    parser.add_argument('-rp', '--report_process', metavar='N', type=str, dest="report_process", default="", help="report process")
    parser.add_argument('-tdr', '--tardiness', action="store_true", dest="tardiness", default=False, help="calculate tardiness of clusters")
    parser.add_argument('-s', '--short', action="store_true", dest="short", default=False, help="short version")
    parser.add_argument('-cae', '--check_assignment_errors', action="store_true", dest="cae", default=False, help="check for potential assignment errors")
    parser.add_argument('-isq', '--check_is_started_quality', action="store_true", dest="isq", default=False, help="check is_started quality")




    return parser.parse_args()

def main():
    """main function"""
    args = parse_arguments()

    if os.path.isfile(args.pegging_csv):
        pegging = Pegging(args.pegging_csv)

    if args.process_info:
        show_process_info(pegging, args.process_info.split(','))
        return 0
    elif args.report_process:
        report_one_proc(pegging, args.report_process)
        return 0
    elif args.cae:
        check_assignment_errors(pegging)
        return 0

    if args.isq:
        materials = get_materials(args.mat_filter)
        check_is_started_quality(pegging, materials)
        return 0

    if args.tardiness:
        for pegging_csv in get_pegging_csf_files(args.pegging_csv):
            pegging = Pegging(pegging_csv)
            print(os.path.basename(pegging_csv))
            report_tardiness(pegging, not args.short)
        return 0

    material_to_check = get_material_to_check(pegging, args.mat_filter)
    #detect_problems_material(pegging, 'K-80', args.threshold_delay, args.same_material)
    detect_problems(pegging, args.threshold_delay, args.dominate_mat, material_to_check)



if __name__ == "__main__":
    try:
        main()
    except BaseException:
        print('Script failed')
        raise
