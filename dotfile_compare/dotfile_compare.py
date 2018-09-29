# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: dotfile_compare.py
#
# description
"""\n\n
    take collector export as input and grep related process ids for given id of type xxx
"""

import sys
import re
import os
    
    
def get_replacement_map(filename):
    mapping = {}
    help_mapping = {}
    # sample line: a13073 [label="a13073 -11250294-0030 PPA 11220863 1 [7808309]",style=filled,fillcolor="white"]
    rgx = re.compile(r"(a\d+)")
    for line in open(filename):
        hit = rgx.search(line)
        while hit:
            act_id = hit.group(1)
            mapping[act_id] = 0
            help_mapping[int(act_id[1:])] = act_id
            
            endpos = hit.end(1)
            line = line[endpos:]
            hit = rgx.search(line)

    keys = help_mapping.keys()
    keys.sort()
            
    for number, key in enumerate(keys):
        new_val = "a%03d" % number
        mapping[help_mapping[key]] = new_val
    return mapping    
     
def get_dst_file(filename):
    dst_dir = os.path.dirname(filename) + "_tmp"
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    return os.path.join(dst_dir, os.path.basename(filename))
     
def get_sorted_keys(mapping):
    length_dict = {}
    for key in mapping:
        length = len(key)
        length_dict.setdefault(length, [])
        length_dict[length].append(key)
    subkeys = length_dict.keys()
    subkeys.sort()
    subkeys.reverse()
    keys = []
    for subkey in subkeys:
        keys.extend(length_dict[subkey])
    return keys
     
def unify_activity_ids(filename):
    mapping = get_replacement_map(filename)
    
    keys = get_sorted_keys(mapping)
    #print keys
   
    stream = open(get_dst_file(filename), "w")
    for line in open(filename):
        for key in keys:
            line = line.replace(key, mapping[key])
        stream.write(line)
    stream.close()
    """
    tmpname = filename + "_tmp"
    out = open(tmpname, "w")
    line_number = -1
    for line in open(filename):
        line_number += 1
        if line_number < svn_info_start or line_number > svn_info_end:
            out.write(line)
    
    out.close()
    os.remove(filename)
    os.rename(tmpname, filename)
    """
    
def main():
    """main function"""
    start_dir = sys.argv[1]
    
    for (path, dirs, files) in os.walk(start_dir):
        src_files = [x for x in files if os.path.splitext(x)[-1] in [".dot"]]
        for src_file in src_files:
            unify_activity_ids(os.path.join(path, src_file))
    

if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
