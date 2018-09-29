# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: accumulate_times.py
#
# description
"""\n\n
    parse optimizer logfile an accumulate times of lines which match given pattern
"""

import sys
import re

def parse_line(line, pattern):
    """parse one single line"""
    hit = re.search(pattern, line)
    if not hit:
        return None
    return line

def parse_logfile(filename, pattern):
    """parse logfile"""
    result = []
    for line in open(filename):
        if line.find("=== Process statistics ====") != -1: # only consider first otpimization
            break
        item = parse_line(line, pattern)
        if item:
            result.append(item)
    return result    

def get_time(line):
    """extract time out of line"""
    hit = re.search(" elapsed msecs: (\d+)", line)
    if hit:
        #print hit.group(1)
        return int(hit.group(1))
    return 0
        
def accumulate(items): 
    """sum up all item times"""
    total_time = 0
    for item in items:
        total_time += get_time(item)
    return total_time       
    
def get_infeasibility_time(filename):
    """get time used on infeasibility"""
    pattern = "end SolInfeasibilityReasoner::TestForInfeasibleProcesses"
    items = parse_logfile(filename, pattern)
    total_time = accumulate(items)
    return total_time

def get_double_items(filename):
    """get 'double' items which have to be stripped later on"""
    pattern = "(TardinessReasoningAfter|TardinessReasoningBefore|end SolTardinessReasoner::GetReasons)"
    items = parse_logfile(filename, pattern)
    return items

def get_after_items(items, pattern):
    """get items which follow an after item"""
    result = []
    for idx in range(0, len(items)-1):
        line = items[idx]
        if line.find(pattern) != -1:
            #print line
            result.append(items[idx+1])
    return result

def get_tardiness_reasoning_after(filename):
    """get time used on tardiness reasoning after"""
    items = get_double_items(filename)
    items = get_after_items(items, "TardinessReasoningAfter")
    total_time = accumulate(items)
    return total_time  

def get_tardiness_reasoning_before(filename):
    """get time used on tardiness reasoning before"""
    items = get_double_items(filename)
    items = get_after_items(items, "TardinessReasoningBefore")
    total_time = accumulate(items)
    return total_time  
    
def main():
    """main function"""
    filename = sys.argv[1]
    
    time_infeasibility = get_infeasibility_time(filename) / 1000.0
    print("time infeasibility reasoning: %f" % time_infeasibility)
    
    time_before = get_tardiness_reasoning_before(filename) / 1000.0
    print("time tardiness reasoning before planning: %f" % time_before)
    
    time_after = get_tardiness_reasoning_after(filename) / 1000.0
    print("time tardiness reasoning after planning: %f" % time_after)

if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise