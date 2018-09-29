# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: delete_unused_regression_files.py
#
# description
"""\n\n
    for given start directory go recursively down and delete unused output files of an regression
"""

import sys
import os
import re
     
def is_obsolete(filename):
    """this are the obsolete files"""
    keys = ['.sdxl', 
            '.lock',
            '_analyzer_activities.csv', 
            '_analyzer_assignments.csv',
            '_analyzer_calendars.csv',
            '_analyzer_depots.csv',
            '_analyzer_partprocesses.csv',
            '_analyzer_precedences.dot',
            '_analyzer_processes.csv',
            '_analyzer_rescals.csv',
            '_analyzer_resources.csv',
            '_proc_activities.csv',
            '_AfterOptimize.xml']
    for key in keys:
        if filename.find(key) != -1:
            return True
    if re.search(r'xToERP.*\.dat', filename):
            return True
    return False
    
def delete_unused_files(start_dir):
    """walk through directory and delete obsolete files"""    
    for (path, dirs, files) in os.walk(start_dir):
        files_to_delete = [x for x in files if is_obsolete(x)]
        for name in files_to_delete:
            os.remove(os.path.join(path, name))
    
def main():
    """main function"""
    start_dir = sys.argv[1]
    
    delete_unused_files(start_dir)
    

if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
