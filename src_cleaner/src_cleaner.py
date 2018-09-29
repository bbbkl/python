# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: src_cleaner.py
#
# description
"""\n\n
    take collector export as input and grep related process ids for given id of type xxx
"""

import sys
import re
import os
     
def strip_svn_info(filename):
    svn_info_start = -1
    svn_info_end = -1
    line_number = -1
    for line in open(filename):
        line_number += 1
        if line.find("subversion (svn) information") != -1:
            svn_info_start = line_number -3
        if line.find("$URL:") != -1:
            svn_info_end = line_number + 1
            break
    #print("handle: %s %d %d" % (filename, svn_info_start,svn_info_end))
    
    if svn_info_start == -1 or svn_info_end == -1:
        return
    
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
    
def findtab(filename):
    for line in open(filename):
        if line.find('\t') != -1:
            return True
    return False    
    
def skip_file(filename):
    """some files have tabs within its testdata - skip such files"""
    skip_files = ['apsMD_ArtikelTest.cpp', 'apsTrMaterialTest.cpp', 'ApsTrProcessTest.cpp']
    return os.path.basename(filename) in skip_files 
    
def untabify(filename):
    if skip_file(filename) or not findtab(filename):
        return
    
    print(filename)
    
    tmpname = filename + "_tmp"
    out = open(tmpname, "w")
    for line in open(filename):
        out.write(line.replace('\t', '  '))
    out.close()
    os.remove(filename)
    os.rename(tmpname, filename) 
    
def main():
    """main function"""
    start_dir = sys.argv[1]
    
    for (path, dirs, files) in os.walk(start_dir):
        src_files = [x for x in files if os.path.splitext(x)[-1] in [".h", ".cpp"]]
        for src_file in src_files:
            fn = os.path.join(path, src_file)
            #strip_svn_info(fn)
            untabify(fn)
    

if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
