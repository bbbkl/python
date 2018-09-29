# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: isolate_bad_process.py
#
# description
"""\n\n
    take file which lists potential bad processes. Generate single proc message file 'name_proc_<xyz>.dat'
    call optimizer for each of these files and report outcome
"""

import sys
import re
import os.path
import subprocess
    
def get_process_ids(filename_ids):
    """split comma separated list of process ids
    """    
    line = open(filename_ids, "r").readline()[:-1]
    process_ids = line.split(',')
    return process_ids
    
def create_dat_file(process_id, filename_dat):
    """call message_file_reader with -f and generate one process dat file"""
    dst = filename_dat.replace(".dat", "_%s.dat" % process_id)
    if os.path.exists(dst):
        return None
    result = subprocess.check_call(["python.exe", r"d:\projects\python\optimizer\message_file_reader.py", "-f", process_id, filename_dat], stdout=sys.stdout)
    if result==0:
        src = filename_dat.replace(".dat", "_stripped.dat")
        os.rename(src, dst)
        return dst
    return None

def call_optimizer(filename_dat):
    """call optimizer for given dat file"""
    output = subprocess.check_output([r"D:\devel\aps_stamm\_apsServer\x64\Rel_Cp16_S8.5\optsrv64.exe", "-DebugLevelLogfile", "1", "-cf", r"D:\devel\Testdaten61\work\optsrv.ini", "-s", "testrunner", \
                                     "-x", "tst", "-offline", "-w", r"D:\devel\Testdaten61\work\output", "-TestMessage", filename_dat])
    if output.find("ERROR") != -1:
        print "Found ERROR in output of file %s" % filename_dat
        sys.exit()
    print "processes %s" % filename_dat
    
def main():
    """main function"""
    filename_ids = sys.argv[1]
    filename_dat = sys.argv[2]
    
    process_ids = get_process_ids(filename_ids)
    for process_id in process_ids:
        proc_datfile = create_dat_file(process_id, filename_dat)
        if proc_datfile is not None:
            call_optimizer(proc_datfile)
    
    

if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
