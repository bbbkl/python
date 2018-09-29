# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: trace_performance.py
#
# description
"""\n\n
    parse optimizer logfile an print all goal calls to console
"""

import sys
import re

def parse_line(line, pattern):
    """parse one single line"""
    hit = re.search(pattern, line)
    if not hit:
        return None
    return hit.group(1)

def parse_logfile(filename, pattern):
    """parse logfile"""
    result = []
    for line in open(filename):
        item = parse_line(line, pattern)
        if item:
            result.append(item)
    return result

def get_level(item):
    """get level, default is 0"""
    hit = re.search(r"level: (\d+)", item)
    if hit:
        return int(hit.group(1))
    return 0

def pprint(items):
    """pretty print items"""
    for item in items:
        level = get_level(item)
        print("%s%s" % (level * '\t', item))
        
def get_format(stats):
    """get format string for stat item"""
    len_goal = 0
    len_count = 0
    len_msecs = 0
    for goal in stats:
        count = stats[goal]["count"]
        msecs = stats[goal]["time"]
        len_goal = max(len_goal, len(goal))
        len_count = max(len_count, len(str(count)))
        len_msecs = max(len_msecs, len(str(msecs)))
    return "%%-%ds\tcount: %%%dd\ttime: %%%dd" % (len_goal, len_count, len_msecs)
        
def make_triples(stats):
    """transform stat into triple elemens: goal, count, time"""
    triples = []
    for goal in stats:
        count = stats[goal]["count"]
        msecs = stats[goal]["time"]      
        triples.append((goal, count, msecs))
    return triples

def sort_by_time(lhs, rhs):
    """sort by time"""
    return sort_by(lhs, rhs, 2)
   
def sort_by_count(lhs, rhs):
    """sort by count"""
    return sort_by(lhs, rhs, 1)

def sort_by(lhs, rhs, idx):
    """sort by value at index"""
    if lhs[idx] < rhs[idx]: 
        return -1
    if lhs[idx] == rhs[idx]: 
        return 0
    return 1

def pprint_stat(stats, compare_by):
    """pretty print items"""
    fmt = get_format(stats)
    triples = make_triples(stats)
    triples = sorted(triples, compare_by, None, True)
    for goal, count, msecs in triples:
        print(fmt % (goal, count, msecs)) 
        
    print("\n")
    total_time = 0
    for goal, count, msecs in triples:
        total_time += msecs
    print(fmt % ("total", 1, total_time))
        
def print_longlasting(items, min_time = 10):
    """print items with time longer than min_time"""
    for item in items:
        time = get_time(item)
        if time >= min_time:
            print item
        
def get_trace(filename):
    """get begin items"""
    pattern = r"begin:\s+(\S.*)"
    return parse_logfile(filename, pattern)        

def get_time_items(filename):
    """get items which contain time info"""
    pattern = r"end:\s+(\S.*(used|elapsed) time: \d+)"
    return parse_logfile(filename, pattern)        

def get_goal(line):
    """extract goal name out of line"""
    hit = re.search("(\S+)::execute", line)
    if hit:
        return hit.group(1)
    return None

def get_time(line):
    """extract time out of line"""
    hit = re.search(" time: (\d+)", line)
    if hit:
        return int(hit.group(1))
    return 0

def make_stat(items):
    """generate statistics goal -> count, time"""
    stats =  {}
    for item in items:
        goal = get_goal(item)
        if goal is None: 
            continue
        time = get_time(item)
        stats.setdefault(goal, {"count" : 0, "time" : 0})
        stats[goal]["count"] += 1
        stats[goal]["time"] += time
    return stats 
        
        
        
    
def main():
    """main function"""
    filename = sys.argv[1]
    
    #items = get_trace(filename)
    #pprint(items)
    
    items = get_time_items(filename)
    stats = make_stat(items)
    pprint_stat(stats, sort_by_time)

    print(2 * "\n")
    pprint_stat(stats, sort_by_count)
    
    print(2 * "\n")
    print_longlasting(items, 10)
    

if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise