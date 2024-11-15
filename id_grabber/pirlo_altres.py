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
from datetime import datetime, timedelta

VERSION = '0.1'


def get_datetime(tp_as_string):
    try:
        # format 2022-10-27 14:59:00
        return datetime.strptime(tp_as_string, '%Y-%m-%d %H:%M:%S')
    except:
        # format 20230508_0252
        return datetime.strptime(tp_as_string, '%Y%m%d_%H%M')

def get_timestamp_key(filename):
    """return YYYYMMDD_HHMM"""
    return re.search(r'^[^_]+_(\d+_\d+)', os.path.basename(filename)).group(1)

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
        base = self.total_tr()
        if base == 0:
            return 0
        return 100 * self.times[key]['tr'] / base

    def pct_te(self, key):
        return 100 * self.times[key]['te'] / self.total_te()

    def print_me(self):
        print("Frequency cnt=%d tr=%0.1f (min) te=%0.1f (min)" % (self.total_cnt(), self.total_tr(), self.total_te()))
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

    def get_num_activities(self):
        tp = self.get_setup_horizon()
        idx = 0
        while idx < len(self.items) and self.items[idx].get_start() < tp:
            idx = idx + 1
        return idx+1

    def get_work_done_horizon(self):
        item = self.items[self.get_num_activities()-1]
        return(item.get_te_accumulated(), item.get_tr_accumulated())

    def get_num_setuptypes(self):
        idx = self.col_lookup['#Different_Setup_Types']
        return int(self.items[0].get_tokens()[idx])

    def get_setup_horizon(self):
        #return get_datetime('2023-03-24 00:00:00')
        idx = self.col_lookup['Setup_Horizon']
        return get_datetime(self.items[0].get_tokens()[idx])

    def get_timepoint_start(self):
        return self.items[0].get_start()

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
                if line.find('FREE') != -1:
                    continue
                tokens = line.split(';')
                if len(tokens) and tokens[0]:
                    items.append(SetupItem(tokens, self.col_lookup))

            # for item in items: print("lack=%s start=%s end=%s" % (item.get_lack(), item.get_start(), item.get_end()))
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
        """a stopper appears on the same ressource more than once with different setup type"""
        return self.stopper

    def get_tokens(self):
        return self.tokens

    def get_idx(self, key):
        try:
            return self.col_lookup[key]
        except KeyError:
            print("get_idx no such key=%s" % key)
            return None

    def get_tr_accumulated(self):
        idx = self.get_idx('Setup_Time_Acc')
        return int(self.tokens[idx])

    def get_te_accumulated(self):
        idx = self.get_idx('Proc_Time_Acc')
        return int(self.tokens[idx])

    def get_te(self):
        try:
            idx = self.get_idx('Proc_Time')
            if idx is not None:
                return int(self.tokens[idx])
        except ValueError:
            pass
        return -1

    def get_tr(self):
        try:
            idx = self.get_idx('Setup_Time')
            if idx is not None:
                return int(self.tokens[idx])
        except ValueError:
            pass
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
    #for proc_id in stopper_ids:
    for proc_id in proc2items.keys():
        # if not is_multi_res_stopper(proc2items[proc_id]): continue
        prev_item = None
        tuples = proc2items[proc_id]
        tuples.sort(key=lambda x: x[1].get_start())
        for idx, item in tuples:
            if prev_item and prev_item.get_lack() == item.get_lack() and prev_item.get_tr() != item.get_tr():
                continue
            #print("{:4d} {:20} {:10} {}".format(idx, item.get_lack() + freq.suffix(item.get_lack()), item.get_res(), item.get_fullact_info()))
            print("{:20} {:10} {}".format(item.get_lack() + freq.suffix(item.get_lack()), item.get_res(), item.get_fullact_info()))
            prev_item = item
        print()


def parse_header(line):
    tokens = line.split(';')
    return tokens #[:-3]


def print_key(key, counters, tr, te, freq):
    res = ''
    for cnt in counters:
        res += "{:6}\t".format(cnt[key] if key in cnt else 0)
    line = '{} {:20} tr={:<5.1f} te={:<5.1f}'.format(res, key + freq.suffix(key), (tr / 60), (te / 60))
    line += '  (cnt %.1f%%, tr %.1f%%, te %.1f%%)' % (freq.pct_cnt(key), freq.pct_tr(key), freq.pct_te(key))
    print(line)


def pretty_print(res2counter, times, freq):
    cnt_all = Counter()
    for cnt in res2counter.values():
        cnt_all.update(cnt)

    key_line = ''
    for key in res2counter.keys():
        key_line += "{:>6}\t".format(key)
    print(key_line)
    for key, cnt in cnt_all.most_common():
        print_key(key, res2counter.values(), times[key]['tr'], times[key]['te'], freq)

def get_csv_pattern_suffix(only_reference, only_result):
    if only_reference and only_result:
        raise Exception("do use -ref or -res and not both together!")
    if only_reference:
        return "reference.csv"
    if only_result:
        return "result.csv"
    return "csv"

def get_csv_files(csv_files, res_filter, only_reference, only_result):
    if len(csv_files) == 1 and os.path.isdir(csv_files[0]):
        candidates = glob(csv_files[0] + "/*.setup_info.*." + get_csv_pattern_suffix(only_reference, only_result))
        if res_filter:
            keys = res_filter.split(',')
            candidates = filter(lambda x: get_res(x) in keys, candidates)
        return candidates
    return csv_files


def make_pairs(csv_files):
    result = {}
    for item in csv_files:
        try:
            key = get_timestamp_key(item)
            result.setdefault(key, []).append(item)
        except AttributeError:
            print("make_pairs, search key failed for '%s'" % item)
            raise
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

def get_day_change_counts(setup_res):
    result = []
    items = setup_res.get_items()
    day_cnt = 0
    val_prev = None
    day_prev = None
    for item in items:
        if val_prev is None:
            val_prev = item.get_lack()
            day_prev = item.get_end()
            continue
        if day_prev.day != item.get_start().day:
            result.append((day_cnt, day_prev))
            day_cnt = 0
            day_prev = item.get_start()
        if val_prev != item.get_lack():
            day_cnt += 1
            val_prev = item.get_lack()
    result.append((day_cnt, day_prev))
    return result

def report_change_freq(setup_res):
    steps = get_day_change_counts(setup_res)
    cnt_all = 0
    day_cnt = 0
    print('change frequency res=%s %s' % (setup_res.get_res(), get_timestamp_key(setup_res.get_path_name())))
    for cnt, timepoint in steps:
        if 0:
            print(cnt, timepoint.strftime('%d.%m.%Y'))
        else:
            day_cnt += 1
            cnt_all += cnt
            print('avg=%0.1f #days=%03d day_change_cnt=%d %s' % (cnt_all/day_cnt, day_cnt, cnt, timepoint.strftime('%d.%m.%Y %a')))

def report_fixed_start(setup_res, stop_after_fixed, freq):
    """"report day + res and condensed sequence of fixed values"""
    headline = setup_res.get_res()
    headline += " %s" % (get_timestamp_key(setup_res.get_path_name()))
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
    report_change_freq(setup_res)
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

def report_transitions(csv_files):
    day_files = make_pairs(csv_files)
    for day in day_files:
        alternatives = []
        for fn in day_files[day]:
            setup_res = SetupRes(fn)
            alternatives.append(setup_res)

        items = []
        for alt in alternatives:
            items.extend(alt.get_items())

        proc2items = {}
        for item in items:
            proc_id = item.get_proc_id()
            proc2items.setdefault(proc_id, [])
            proc2items[proc_id].append(item)

        counters = Counter()
        for proc_id in proc2items.keys():
            prev_val = None
            items = proc2items[proc_id]
            items.sort(key=lambda x: x.get_start())
            for item in items:
                val = item.get_lack()
                if val != prev_val:
                    transition = "{:23} {:23}".format(str(prev_val), val)
                    counters[transition] += 1
                    prev_val = val
        print(day)
        for key, cnt in counters.most_common():
            print("{:3d} {}".format(cnt, key))
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

def get_matrix_transition(tokens):
    time, cost = tokens[2:4]
    property_type = tokens[4]
    val_from = val_to = None
    if property_type == '2': # assembly_part_feature
        val_from = '/'.join(map(lambda x: x.strip(), tokens[5:8]))
        val_to = '/'.join(map(lambda x: x.strip(), tokens[14:17]))
    elif property_type == '3': # bomline_part
        val_from = tokens[8]
        val_to = tokens[17]
    elif property_type == '4': # Resource
        val_from = tokens[12]
        val_to = tokens[21]
    elif property_type == '5': # operation_class
        val_from = tokens[10]
        val_to = tokens[19]
    else:
        raise 'unhandled property type %s' % property_type
    return "{:<15} {:<15} time={:<5} cost={:<}".format(val_from, val_to, time, cost)

def report_matrix_values(msg_file):
    with open(msg_file) as istream:
        data = None
        matrix2values = {}
        matrix2Percent = {}
        matrixHeader = {}
        matrix2Transition = {}
        for line in istream:
            # 2	396	DEF_ERPCommandcreate_SetupMatrixEn
            if line.find('2') == 0 and line.find('396') == 2 and data is not None:
                tokens = data.split('\t')
                matrix_id = tokens[1]
                matrix2Transition.setdefault(matrix_id, set())
                matrix2Transition[matrix_id].add(get_matrix_transition(tokens))
                property_type, values = get_matrix_values(tokens)
                if property_type:
                    matrix2values.setdefault(matrix_id, {})
                    matrix2values[matrix_id].setdefault(property_type, set()).update(values)
                matrix2Percent.setdefault(matrix_id, set())
                pct = int(tokens[2])
                if pct:
                    matrix2Percent[matrix_id].add(pct)
            elif line.find('2') == 0 and line.find('395') and data is not None:
                tokens = data.split('\t')
                matrixHeader[tokens[1]] = tokens[2:]

            elif line.find(r'3') == 0:
                data = line[:-1]
        for mid in matrix2values:
            print('\nmatrix=%s (%d) pct=%s horizon=%s interval=%s default_cost=%s' % (mid, len(matrix2values[mid]), sorted(matrix2Percent[mid]), *matrixHeader[mid]))
            for property_type in matrix2values[mid]:
                print('\tproperty_type=%s' % property_type)
                for idx, val in enumerate(sorted(matrix2values[mid][property_type])):
                    print('\t\t% 3d "%s"' % (idx, val))
                print()
            for item in sorted(matrix2Transition[mid]):
                print('\t\t%s' % item)
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
                    res2matrix.setdefault(res_id, set())
                    res2matrix[res_id].add(matrix_id)
            elif line.find('3') == 0:
                data = line[:-1]
    for res, matrix_ids in sorted(res2matrix.items()):
        print('res=%s matrix=%s' % (res, ', '.join(matrix_ids)))

def show_header_infos(csv_files):
    for fn in csv_files:
        setup_res = SetupRes(fn)
        print(fn)
        val_te, val_tr = setup_res.get_work_done_horizon()
        print("#act=%d sum_tr=%d sum_te=%d #diff_vals=%d horizon=%s\n" % (setup_res.get_num_activities(), val_tr, val_te, setup_res.get_num_setuptypes(), setup_res.get_setup_horizon()))

def show_setup_quality(csv_files):
    rgx = re.compile('setup_info.7.([^\.]+)')
    pairs = make_pairs(csv_files)
    for key in pairs:
        print("\n\n%s %s %s" % (5 * "=", key, 25 * "="))
        files = sorted(pairs[key], key=lambda x: rgx.search(x).group(1))
        show_header_infos(files)

def get_setup_costs(csv_file):
    with open(csv_file) as istream:
        for line in istream:
            hit = re.search(r'^;+(\d+)', line)
            if hit:
                return int(hit.group(1))
    return -1

def make_tuple(csv_files):
    result = {}
    handled = []
    rgx = re.compile('setup_info.7.([^\.]+)')
    for fn in csv_files:
        hit = rgx.search(fn)
        if hit and not hit.group(1) in handled:
            key = hit.group(1)
            files = list(filter(lambda x: x.find(key) != -1, csv_files))
            if len(files) == 2:
                result[key] = files
    return result

def get_qinfo(items, timepoints):
    result = []
    for timepoint in timepoints:
        ref_item = items[0]
        for item in items:
            if item.get_start() <= timepoint:
                ref_item = item
            else:
                break
        result.append([ref_item.get_tr_accumulated(), ref_item.get_te_accumulated()])
    return result

def pprint_qinfo(check_days, vals_ref, vals_res):
    for pfx, values in [('ref', vals_ref), ('res', vals_res)]:
        line = "%s days " % pfx
        for i, day in enumerate(check_days):
            if i>0:
                line += ", "
            line += "{:>3}: tr={:<5} te={:<5}".format(day, values[i][0], values[i][1])
        print(line)


def setup_compare(csv_files, check_days):
    rgx = re.compile('setup_info.7.([^\.]+)')
    pairs = make_pairs(csv_files)
    for key in pairs:
        tp = get_datetime(key)
        tps = list(map(lambda x: tp + timedelta(days=x), check_days))
        print("\n\n%s %s %s" % (5 * "=", key, 25 * "="))
        tuples = make_tuple(pairs[key])
        for res in tuples:
            file_ref = tuples[res][0]
            file_res = tuples[res][1]

            q_ref = get_qinfo(SetupRes(file_ref).get_items(), tps)
            q_res = get_qinfo(SetupRes(file_res).get_items(), tps)
            val_ref = get_setup_costs(file_ref)
            val_res = get_setup_costs(file_res)
            print("{:<6} total_setup_cost ref={:<7} res={:<}".format(res, val_ref, val_res))
            pprint_qinfo(check_days, q_ref, q_res)
            print()

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
    parser.add_argument('-q', '--quality', action="store_true",  # or stare_false
                        dest="quality", default=False,  # negative store value
                        help="compare setup quality")
    parser.add_argument('-ref', '--reference_only', action="store_true",  # or stare_false
                        dest="reference_only", default=False,  # negative store value
                        help="use only refence csv files")
    parser.add_argument('-res', '--result_only', action="store_true",  # or stare_false
                        dest="result_only", default=False,  # negative store value
                        help="use only result csv files")
    parser.add_argument('-c', '--compare', metavar='string',
                        dest="setup_compare", default='',
                        help="if non-empty, show setup quality for given days, e.g. 10,20,30")
    parser.add_argument('-s', '--short_version', action="store_true",  # or stare_false
                        dest="short_version", default=False,  # negative store value
                        help="report short version of fixed start values, start - end value #items")
    parser.add_argument('-m', '--maxtrix_values', metavar='string',
                        dest="matrix_values", default='',
                        help="report setup matrix values for given messagefile")
    parser.add_argument('-t', '--transitions', action="store_true",  # or stare_false
                        dest="show_transitions", default=False,  # negative store value
                        help="report transitions")
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

    csv_files = get_csv_files(args.csv_files, args.res_filter, args.reference_only, args.result_only)

    if args.setup_compare:
        check_days = [int(x) for x in args.setup_compare.split(',')]
        setup_compare(csv_files, check_days)
        return 0

    if args.quality:
        show_setup_quality(csv_files)
        return 0

    if args.show_transitions:
        report_transitions(csv_files)
        return 0

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
