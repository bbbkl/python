# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: priochanger.py
#
# description
"""\n\n
    take a *.dat file an change priority of contained processes
"""

import sys
import re
import os.path

def tokenize(dataline):
    return dataline.split('\t')

def is_head(dataline_process):
    """for a process dataline return true, if line describes a head process, false otherwise"""
    tokens = tokenize(dataline_process)
    return tokens[17] == '1'

def get_prio(dataline_process):
    return tokenize(dataline_process)[11]

def get_produced_part(dataline_process):
    return tokenize(dataline_process)[4]

def change_prio(dataline_process, new_prio):
    tokens = tokenize(dataline_process)
    tokens[11] = new_prio
    return '\t'.join(tokens)

def change_priorities(filename, nth, new_prio):
    """go through datfile and call for each head process a special fct"""
    tmp_file = filename + ".tmp"
    stream = open(tmp_file, "w")
    
    process_count = 0
    dataline = None
    counterlines = []
    for line in open(filename):
        if line.find('2\t370') == 0: # only consider first otpimization
            if dataline != None and is_head(dataline):
                process_count += 1
                if process_count % nth == 0:
                    dataline = change_prio(dataline, new_prio)
        
        if line.find('4\t') == 0:
            counterlines.append(line)
            continue
        
        if line.find('3\t') == 0:
            if dataline is not None:
                stream.write(dataline)
            if counterlines is not None:
                for item in counterlines:
                    stream.write(item)
                counterlines = []
            dataline = line
            continue
        
        
        
        if dataline is not None:
            stream.write(dataline)
            dataline = None
        if counterlines is not None:
            for item in counterlines:
                stream.write(item)
            counterlines = []
        stream.write(line)
    
    if dataline is not None:
        stream.write(dataline)
    if counterlines is not None:
        for item in counterlines:
            stream.write(item)
            
    stream.close()
    
    tmp_file2 = filename + ".tmp2"
    os.rename(filename, tmp_file2)
    os.rename(tmp_file, filename)
    os.remove(tmp_file2)
 
def split_prio_directive(prio_directive):
    """expected format: nn:prio"""
    num, prio = prio_directive.split(':')
    return int(num), prio
 
def main():
    """main function"""
    filename = sys.argv[1]
    prio_directive = sys.argv[2]
    
    nth, new_prio = split_prio_directive(prio_directive)
    change_priorities(filename, nth, new_prio)

if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
