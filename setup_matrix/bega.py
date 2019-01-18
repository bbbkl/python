# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: bega.py
#
# description
"""\n\n
    evaluate bega setup data
"""

import sys
import re
import os
from glob import glob
from datetime import datetime
from argparse import ArgumentParser
from operator import itemgetter

VERSION = '0.1'

def test_encoding(filename):
    """check for file encoding"""
    encodings = ["UTF-8", "ISO-8859-1", "latin-1"]
    
    if not os.path.exists(filename):
        raise FileNotFoundError(filename)
    
    for item in encodings:
        try:
            for line in open(filename, encoding=item):
                pass
            return item
        except:
            pass
        
    raise ("Cannot get right encoding, tried %s" % str(encodings))

class ResInfo:
    def __init__(self, tokens):
        self._tokens = tokens # dict mrp_area -> dispo_parameter

    def __str__(self):
        text = "%s res=%s/%s is_alt=%s is_base=%s" % (self.id(), self.res_kind(), self.res(), self.alt_res(), self.base_res())
        return text

    """
    TrResource    LA-00006282 22371 105709 H0110 
     1 process_area     PPA
     2 process          LA-00006282
     3 part_process     22371
     4 act_pos          60
     5 res_pos          10
     6 res_kind         2 (Mensch)
     7 res              H0110
     8 ident_act        105709
     9 intensity        1
    10 alt_group        0
    11 base_res         0
    12 selected_res     
    13 overload_used    1
    """
    
    def process(self):
        return self._tokens[2]
    def partproc(self):
        return self._tokens[3]
    def actpos(self):
        return self._tokens[4]
    def id(self):
        return ("%s/%s/%s" % (self.process(), self.partproc(), self.actpos()))
    def res_pos(self):
        return self._tokens[5]
    def res_kind(self):
        return self._tokens[6]
    def res(self):
        return self._tokens[7]
    def alt_res(self):
        return self._tokens[10]
    def is_alt_res(self):
        return self._tokens[10] == '1'
    def base_res(self):
        return self._tokens[11]
    def is_base_res(self):
        return self._tokens[11] == '1'
    def set_base_res(self, new_val):
        self._tokens[11] = new_val
    def dataline(self):
        return '\t'.join(self._tokens)
        
def get_datetime_from_string(str_time):
    try:
        # format 2018-11-30 01:21:00
        return datetime.strptime(str_time, '%Y-%m-%d %H:%M:%S')
    except:
        # format 13.11.2018 13:03
        return datetime.strptime(str_time, '%d.%m.%Y %H:%M')
        
def show_non_mofas(setup_file):
    """get total numer of different values. show stat value -> #number"""
    rgx = re.compile(r'ActivityClass/\d')
    
    for line in open(setup_file):
        hit = rgx.search(line)
        if(hit):
            print(line[:-1])
    sys.exit(0)
            
def discard_procs_without_other_baseres_candidate(procToRes, src_res_id):
    procs_to_discard = []
    for proc in procToRes:
        proc_ok = False
        resources = procToRes[proc]
        for res in resources:
            if res.res() != src_res_id and res.res_kind()=='1':
                proc_ok = True
        if not proc_ok:
            procs_to_discard.append(proc)
    print("procs to discard #=%d %s" % (len(procs_to_discard), procs_to_discard))
    for proc in procs_to_discard:
        del procToRes[proc]

def parse_resources(filename):
    resources = []
    dataline = None
    for line in open(filename):
        if re.search('^2\s350', line):
            if dataline is not None:
                res_item = ResInfo(dataline.split('\t'))
                resources.append(res_item)
                dataline = None
                continue
        if re.search(r'^(1\t)?3\t', line):
            dataline = line
    return resources
    
def change_base_res(messagefile, procToRes, src_res_id):
    new_file = messagefile.replace('.dat', '.base_res_changed.dat')
    out = open(new_file, "w")
    dataline = None
    dataline_written = None
    for line in open(messagefile):
        if re.search('^2\s350', line):
            if dataline is not None:
                res_item = ResInfo(dataline.split('\t'))
                id = res_item.id()
                kind = res_item.res_kind()
                if id in procToRes and (kind=='1' or kind=='2'):
                    new_val = '0' if res_item.res() == src_res_id else '1'
                    res_item.set_base_res(new_val)
                out.write(res_item.dataline())
                out.write(line)
                dataline = None
                continue
        if dataline is not None and dataline != dataline_written:
            out.write(dataline)
            dataline_written = dataline
        if line[0] != '3':
            out.write(line)
        if re.search(r'^(1\t)?3\t', line):
            dataline = line
    out.close()
    
def calculate_cost(filename):
    """cost are in the nth column of the csv file, summarize them"""
    nth = None
    firstLine = True
    total_cost = 0
    for line in open(filename):
        tokens = line.split(';')
        if firstLine:
            firstLine = False
            nth = tokens.index('Setup_Properties_Change')
            continue
        try:
            cost = int(tokens[nth])
            total_cost += cost
        except:
            pass # ignore
    return total_cost
    
def find_setup_files(start_dir, extension=".result.csv"):
    """for given dir find all files which match extension"""    
    setup_files = []
    for root, dirs, files in os.walk(start_dir):
        tmp = [x for x in files if x.find(extension) != -1 and x.find('setup_info') != -1]
        setup_files.extend([os.path.join(root, x) for x in tmp])
    return setup_files
    
def get_first_level_dir(filename):
    """short name = last dir + filename"""
    return os.path.basename(os.path.dirname(filename)) 

def get_interval_and_horizon(filename):
    """both values are encoded in the dirname"""
    dirname = os.path.basename(os.path.dirname(filename))
    hit = re.search('_(\d+)_(\d+)$', dirname)
    if hit:
        return int(hit.group(1)), int(hit.group(2))
    return (0, 0)  

def get_resource(filename):
    name = os.path.basename(filename)
    hit = re.search('setup_info\.(\d+\.\d+)', name)
    return hit.group(1).replace('.', '/')    
   
def get_value_count(filename):
    """get number of values for given setup resource csv file"""
    firstLine = True
    for line in open(filename):
        tokens = line.split(';')
        if firstLine:
            firstLine = False
            nth = tokens.index('#Activities')
            continue
        return int(tokens[nth])
 
def get_setup_horizon(filename):
    first_line = True
    for line in open(filename):
        tokens = line[:-1].split(';')
        if first_line:
            first_line = False
            idx_horizon = tokens.index('Setup_Horizon')
        else:
            return tokens[idx_horizon]
 
def get_range_stat(filename):
    """get number of values with start before given timepoint and accumulated work"""
    timepoint = get_setup_horizon(filename)
    deadline = get_datetime_from_string(timepoint)
    first_line = True
    idx_start = idx_work = idx_cost = None
    range_count = 0
    range_work = 0
    range_cost = 0
    for line in open(filename):
        tokens = line.split(';')
        if first_line:
            first_line = False
            idx_start = tokens.index('Start')
            idx_work = tokens.index('Proc_Time_Acc')
            idx_cost = tokens.index('Setup_Properties_Change')
            continue
        start = tokens[idx_start]
        if get_datetime_from_string(start) > deadline:
            break
        range_count += 1
        range_cost += int(tokens[idx_cost])
        range_work = int(tokens[idx_work])
    return range_count, range_work, range_cost
  
def grep_data(logfile, keys):
    """grep phase4 quality relevant data out of logfile"""
    stream = open(logfile)
    info = parse_head_info(stream, keys)
    return info  
   
def parse_head_info(stream, keys):
    rgx_dict = make_regex(keys)
    rgxDone = []
    key_flag = False
    result = {}
    while stream:
        line = stream.readline()
        key_flag |= line.find('=== Processing statistics ====') != -1
        if key_flag:
            for rgx in rgx_dict:
                if rgx in rgxDone:
                    continue
                hit = rgx.search(line)
                if hit:
                    result[rgx_dict[rgx]] = hit.group(2)
                    rgxDone.append(rgx)
            if len(result) == len(keys):
                return result
    return result

def make_regex(keys):
    result = {}
    for key in keys:
        rgx = re.compile(r'(%s)(?:.*:)?\s*(\S+)' % key)
        result[rgx] = key
    return result   

def add_step_durations(logfile, stat):
    """
    SetupOpt: Step 1 - initial optimization needed 188323 milliseconds
    SetupOpt: Step 2a - setup optimization - subsequences needed 491119 milliseconds
    SetupOpt: Step 2b - setup optimization - whole sequences needed 1119877 milliseconds

    """
    result = ''
    rgx = re.compile(r'SetupOpt: (Step \S+).*\s(\d+) milliseconds')
    for line in open(logfile):
        hit = rgx.search(line)
        if hit:
            if not len(result) == 0:
                result += ', '
            step = hit.group(1).replace(' ', '_')
            secs = int(hit.group(2)) / 1000
            result += '%s=%d' % (step, secs)
    stat['steps'] = result
    
def parse_logfile(logfile):
    """parse duration, quality values out of given logfile"""
    keys = ['Total proc. time with breaks', 'DLZ partproc with breaks total', 
            'Lateness total', 'Earliness total', 'computing time.*\(',
            'early:', 'in time:', 'delayed:',]
    result = grep_data(logfile, keys)
    add_step_durations(logfile, result)
    
    return result
  
def pretty_print_accumulated_setup_stats(resourceToValues, log_stats):   
    """res id -> first level dir, interval, horizon, cost, count, range count, range cost, range work"""
    idToSum = {}
    for res in sorted(resourceToValues):
        if res[0] != '1':
            continue
        for dirname, interval, horizon, cost, count, range_count, range_work, range_cost in resourceToValues[res]:
            idToSum.setdefault(dirname, {'interval' : 0, 'horizon': 0, 'cost' : 0, 'count' : 0, 'range_count' : 0, 'range_work' : 0, 'range_cost' : 0})
            #sumStat = idToSum[dirname]
            idToSum[dirname]['interval'] = interval
            idToSum[dirname]['horizon'] = horizon
            
            idToSum[dirname]['cost'] += cost
            idToSum[dirname]['count'] += count
            idToSum[dirname]['range_count'] += range_count
            idToSum[dirname]['range_work'] += range_work
            idToSum[dirname]['range_cost'] += range_cost
    
    print('\nresources 00410 - 00415 + 00466 - 00468')
    print('dirname;interval;horizon;total_cost;total_values;range_values;range_cost;range_work;Earliness;Lateness;#early;#in_time;#delayed;execution_time;step_times (secs)')
    sorted_keys = sorted(idToSum)
    key = 'without_setup_opti'
    if key in sorted_keys:
        sorted_keys.remove(key)
        sorted_keys.insert(0, key)
    for name in sorted_keys:
        sub_stat = idToSum[name]
        i = sub_stat['interval']
        h = sub_stat['horizon']
        c = sub_stat['cost']
        cnt = sub_stat['count']
        r_cnt = sub_stat['range_count']
        r_wrk = sub_stat['range_work']
        r_cost = sub_stat['range_cost']
        
        log_stat = log_stats[name]
        earliness = log_stat['Earliness total']
        lateness = log_stat['Lateness total']
        early = log_stat['early:']
        in_time = log_stat['in time:']
        delayed = log_stat['delayed:']
        elapsed = log_stat['computing time.*\(']
        elapsed = elapsed[0: elapsed.find('.')]
        steps = log_stat['steps']
        print("%s;%d;%d;%d;%d;%d;%d;%d;%s;%s;%s;%s;%s;%s;%s" % (name, i, h, c, cnt, r_cnt, r_cost, r_wrk,
            earliness, lateness, early, in_time, delayed, elapsed, steps)) 
  
def get_logfile(dirname, extension):
    files = glob(dirname + '/*%s' % extension)
    if len(files) == 0:
        return ''
    return files[0]
  
def calc_log_stats(setup_files, log_stats, single=False):
    for fn in setup_files:
        short_name = get_first_level_dir(fn)
        log_file = get_logfile(os.path.dirname(fn), '.result.log')
        if not os.path.exists(log_file):
            log_file = get_logfile(os.path.dirname(fn), '.log')
        log_stats[short_name] = parse_logfile(log_file)    
        
    if not single:
        fn1 = setup_files[0]
        log_file = get_logfile(os.path.dirname(fn1), '.reference.log')
        log_stats['without_setup_opti'] = parse_logfile(log_file)
  
def pretty_print_setup_stats(resourceToValues, log_stats = None):   
    """res id -> first level dir, interval, horizon, cost"""
    if log_stats is None:
        for res in sorted(resourceToValues):
            print('\n%s' % res)
            print('dirname;interval;horizon;total_cost;total_values;range_values;range_cost;range_work')
            for dirname, interval, horizon, cost, count, range_count, range_work, range_cost in resourceToValues[res]:
                print("%s;%d;%d;%d;%d;%d;%d;%d" % (dirname, interval, horizon, cost, count, range_count, range_cost, range_work))
    else:
        for res in sorted(resourceToValues):
            print("\n'%s'" % res)
            print('dirname;interval;horizon;total_cost;total_values;range_values;range_cost;range_work;Earliness;Lateness;#early;#in_time;#delayed;execution_time;step_times (secs)')
            for name, interval, horizon, cost, count, range_count, range_work, range_cost in resourceToValues[res]:
                log_stat = log_stats[name]
                earliness = log_stat['Earliness total']
                lateness = log_stat['Lateness total']
                early = log_stat['early:']
                in_time = log_stat['in time:']
                delayed = log_stat['delayed:']
                elapsed = log_stat['computing time.*\(']
                elapsed = elapsed[0: elapsed.find('.')]
                steps = log_stat['steps']
                print("%s;%d;%d;%d;%d;%d;%d;%d;%s;%s;%s;%s;%s;%s;%s" % (name, interval, horizon, cost, count, range_count, range_cost, range_work,
                    earliness, lateness, early, in_time, delayed, elapsed, steps)) 
    
def pretty_print_value_stat(value_stat):
    for key in sorted(value_stat):
        line = key
        resToCnt = value_stat[key]
        for res in sorted(resToCnt):
            if res.find('_value') != -1: 
                continue
            #line += ";%s=%d" % (res, resToCnt[res])
            line += ";%d" % resToCnt[res]
        print(line)
    
def get_proc_id(act_name):
    keys = ('PPA', 'PPN', 'CDD')
    for key in keys:
        idx = act_name.find(' ' + key)
        if idx != -1:
            break
    proc_id = act_name[:idx]
    return proc_id
    
def pretty_print_value_stat2(value_stat, proc_info):
    for key in sorted(value_stat):
        resToCnt = value_stat[key]
        for res in sorted(resToCnt):
            if res.find('_value') != -1: 
                continue
            print("\nval=%s res=%s cnt=%d" % (key, res, resToCnt[res]))
            items = value_stat[key][res + "_values"]
            last_item_idx = 3
            for item in items:
                act = item[0]
                proc_id = get_proc_id(act)
                item.append(proc_info[proc_id]['duedate'])
                item.append(proc_info[proc_id]['prio'])
            items = sorted(items, key=itemgetter(3)) # 3 - duedate, 1 - start
            for item in items:
                print('\tact=%-30s fix=%s prio=%-3s duedate=%s start=%s end=%s' % (item[0], item[3], item[last_item_idx+2], item[last_item_idx+1], item[1], item[2]))
                # excel like output
                #print('%s;%s;%s;%s;%s' % (item[0], item[4].replace('.', ','), item[3], item[1], item[2]))
    
def guess_schedinfo_file(setup_files):
    fn = setup_files[0]
    fn = fn[:fn.find('.setup_info')]
    fn += '.schedInfo.result.csv'
    if not os.path.exists(fn):
        candidates = glob(os.path.dirname(fn) + "/*schedInfo.csv")
        if len(candidates) == 1:
            fn = candidates[0]
    return fn    
    
def guess_headproc_file(setup_files):
    fn = setup_files[0]
    fn = fn[:fn.find('.setup_info')]
    fn += '.headproc_result.csv'
    return fn
  
def get_proc_info(setup_files):
    result = {}
    headproc_file = guess_schedinfo_file(setup_files)
    idx_proc = idx_duedate = idx_prio = -1
    for line in open(headproc_file):
        tokens = line.split(';')
        if line.find('process;') != -1:
            idx_proc = tokens.index('process')
            idx_duedate = tokens.index('due_date')
            idx_prio = tokens.index('priority_erp')
            continue

        if len(tokens) > 2:
            proc_id = tokens[idx_proc][4:]
            due_date = tokens[idx_duedate]
            prio = tokens[idx_prio]
            result[proc_id] = {'duedate' : due_date, 'prio' : prio }
            #print(proc_id, due_date, prio)
    return result
    
def cal_value_stat(setup_files): 
    valueStat = {}
    for fn in setup_files:
        encoding_id = test_encoding(fn)
        res = get_resource(fn)
        res_val = res + "_values"
        firstLine = True
        nth = None
        for line in open(fn, encoding=encoding_id):
            tokens = line.split(';')
            if firstLine:
                firstLine = False
                nth = tokens.index('Setup_Properties')
                continue
            if len(tokens) > nth:
                val = tokens[nth]
                #print(val, res)
                valueStat.setdefault(val, {})
                valueStat[val].setdefault(res, 0)
                valueStat[val][res] += 1
                valueStat[val].setdefault(res_val, [])
                fixed = '1' if tokens[4] == 'true' else '0'
                valueStat[val][res_val].append([tokens[0], tokens[1], tokens[2], fixed])
    pretty_print_value_stat(valueStat)
    pretty_print_value_stat2(valueStat, get_proc_info(setup_files))
    

"""
def getDurations(setup_file):
    durations = []
    idx_start = idx_end = idx_proctime = None
    firstLine = True
    encoding_id = test_encoding(setup_file)
    for line in open(setup_file, encoding=encoding_id):
        tokens = line.split(';')
        if firstLine:
            idx_start = tokens.index('Start')
            idx_end= tokens.index('End')
    
    return durations  
"""   
    
def calc_setup_stats(setup_files, stats):
    """
    for each setup file get resource, interval, horizon, cost
    pretty print this stat
    """
    for setup_file in setup_files:
        short_name = get_first_level_dir(setup_file)
        interval, horizon = get_interval_and_horizon(setup_file)
        resource = get_resource(setup_file)
        cost = calculate_cost(setup_file)
        value_count = get_value_count(setup_file)
        # 60 days range
        range_count, range_work, range_cost = get_range_stat(setup_file)
        #durations = getDurations(setup_file)
        
        stats.setdefault(resource, [])
        stats[resource].append((short_name, interval, horizon, cost, value_count, range_count, range_work, range_cost))
    return stats

def filter_the_reference_files(candidates):
    """from a bunch of reference files find the files which have the directory in common"""
    result = []
    if len(candidates) > 0:
        dirname = os.path.dirname(candidates[0])
        result = [x for x in candidates if os.path.dirname(x) == dirname]
    return result

def add_reference_info(start_dir, setup_stats):
    resToCost = {}
    reference_files = find_setup_files(start_dir, ".reference.csv")
    reference_file = filter_the_reference_files(reference_files)
    for fn in reference_files:
        #if fn.find('_20180625_')==-1: 
        #    continue
        resource = get_resource(fn)
        cost = calculate_cost(fn)
        value_count = get_value_count(fn)
        #print(value_count, resource, fn)
        range_count, range_work, range_cost = get_range_stat(fn)
        resToCost[resource] = (cost, value_count, range_count, range_work, range_cost)
    for res in resToCost:
        cost, value_count, rg_cnt, rg_wrk, rg_cost = resToCost[res]
        setup_stats.setdefault(res, [])
        setup_stats[res].append(('without_setup_opti', 0, 0, cost, value_count, rg_cnt, rg_wrk, rg_cost))
        #print('%s %d' % (res, resToCost[res]))
    #sys.exit(0)
    return setup_stats
        
def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('-c', '--cost',  action="store_true", # or store_false
                      dest="cost", default=False, # negative store value
                      help="calculate setup cost for given csv setup file")
    parser.add_argument('-cs', '--cost_result',  action="store_true", # or store_false
                      dest="cost_result", default=False, # negative store value
                      help="calculate setup cost for given csv result setup files")
    parser.add_argument('-vs', '--value_stats',  action="store_true", # or store_false
                      dest="value_stats", default=False, # negative store value
                      help="calculate value distributeion statistics")
    parser.add_argument('value_file', metavar='value_file', help='input value file')
    
    return parser.parse_args()

def main():
    """main function"""
    args = parse_arguments()
    filename = args.value_file

    #show_non_mofas(filename)
    #return 

    if args.cost:
        start_dir = filename
        setup_files = find_setup_files(start_dir)
        setup_stats = {}
        setup_stats = add_reference_info(start_dir, setup_stats)
        setup_stats = calc_setup_stats(setup_files, setup_stats)
        
        log_stats = {}
        calc_log_stats(setup_files, log_stats)
        
        bega = 1 if setup_files[0].find('bega') else 0
        if bega:
            pretty_print_accumulated_setup_stats(setup_stats, log_stats)
            pretty_print_setup_stats(setup_stats)
        else:
            pretty_print_setup_stats(setup_stats, log_stats)
        return
    
    if args.cost_result:
        start_dir = filename
        setup_files = find_setup_files(start_dir)
        setup_stats = {}
        setup_stats = calc_setup_stats(setup_files, setup_stats)
        
        log_stats = {}
        calc_log_stats(setup_files, log_stats, True)
        
        bega = 1 if setup_files[0].find('bega') else 0
        if bega:
            pretty_print_accumulated_setup_stats(setup_stats, log_stats)
            pretty_print_setup_stats(setup_stats)
        else:
            pretty_print_setup_stats(setup_stats, log_stats)
        return
    
    if args.value_stats:
        start_dir = filename
        setup_files = find_setup_files(start_dir)
        cal_value_stat(setup_files)
        return
    
    resources = parse_resources(filename)
    procToRes = {}
    base_id = 'H0410'
    for res in resources:
        if res.res() == base_id:
            procToRes[res.id()] = [res,]
    
    for res in resources:
        if res.res() != base_id and res.id() in procToRes:
            procToRes[res.id()].append(res)
    
    #print("#procs before discard=%d" % len(procToRes))
    discard_procs_without_other_baseres_candidate(procToRes, base_id)
    #print("#procs after discard=%d" % len(procToRes))
    
    #change_base_res(filename, procToRes, base_id)
    #return
    
    print('critical processes')    
    cnt = 1
    for proc in procToRes:
        resources = procToRes[proc]
        print("%d %s" % (cnt, proc))
        cnt += 1
        for res in resources:
            print('\t%s' % res)
    
    #eturn
    
    print('\nprocesses with only one resource')    
    cnt = 1
    for proc in procToRes:
        resources = procToRes[proc]
        if len(resources) == 1:
            print('%d %s' % (cnt, resources[0]))
            cnt += 1

    print("\nprocesses with only one non-altres resource")    
    cnt = 1
    for proc in procToRes:
        resources = procToRes[proc]
        if len(resources) == 1:
            continue
        with_alt_res = False
        for res in resources:
            if res.is_alt_res():
                with_alt_res = True
                break
        if not with_alt_res:
            print('%d %s' % (cnt, proc))
            cnt += 1
            for res in resources:
                if res.res() == base_id:
                    continue
                print('\t%s' % res)


    print("\nprocesses with one altres group")    
    cnt = 1
    for proc in procToRes:
        resources = procToRes[proc]
        if len(resources) == 1:
            continue
        with_alt_res = False
        for res in resources:
            if res.is_alt_res():
                with_alt_res = True
                break
        if with_alt_res:
            print('%d %s' % (cnt, proc))
            cnt += 1
            for res in resources:
                if res.res() == base_id:
                    continue
                print('\t%s' % res)

if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
