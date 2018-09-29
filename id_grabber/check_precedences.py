# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: check_precedences.py
#
# description
"""\n\n
    check for dublicates in precedences of given message file
"""

import sys
import re

def report_potential_dublicates(id_to_linecnt):
    """check for linecount with distance less than n"""
    done_flag = 0
    for precedence_id in id_to_linecnt:
        counters = id_to_linecnt[precedence_id]
        previous_counter = counters[0]
        for counter in counters[1:]:
            diff = counter - previous_counter
            if diff < 100:
                print("potential precedence dublicate %s, lines %d, %d" % (precedence_id, previous_counter, counter))
                done_flag = 1
            previous_counter = counter        

    if done_flag:
        print("\n")

def get_id(dataline, line_cnt):
    """id = partproc_from/id_act_from - partproc_to/id_act_to"""
    tokens = dataline.split('\t')
    if len(tokens) < 6:
        print("Bad line %d, '%s'" % (line_cnt, dataline))
        return None
    return "%s/%s - %s/%s" % (tokens[3], tokens[4], tokens[5], tokens[6])

def check_precedences(messagefile):
    """check for dublicates in precedences"""
    line_cnt = -1
    previous_line = None
    rgx_trconstraint = re.compile(r'^2\t360') # 360 = DEF_ERPCommandcreate_Constraint___
    rgx_break = re.compile(r'2\t(120|121|122|123|124|196|197)') # 120 = optimize, 121 = DEF_ERPCommandoptimizeCTP_________, 196=sync
    
    id_to_linecnt = {}
    
    for line in open(messagefile):
        line_cnt += 1
        hit = rgx_break.search(line)
        if hit:
            report_potential_dublicates(id_to_linecnt)
            id_to_linecnt = {}
            previous_line = None
            continue
        
        hit = rgx_trconstraint.search(line)
        if hit and previous_line is not None:
            precedence_id = get_id(previous_line, line_cnt)
            if precedence_id is not None:
                id_to_linecnt.setdefault(precedence_id, [])
                id_to_linecnt[precedence_id].append(line_cnt)
                continue
        previous_line = line
    
    report_potential_dublicates(id_to_linecnt)
    
def main():
    """main function"""
    filename = sys.argv[1]
    
    check_precedences(filename)

if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
