# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: repair_logfilenames.py
#
# description
"""\n\n
    for given start directory go recursively down and check and repair logfiles
"""
import sys
import os

def get_name_datfile(files):
    """this are the dat file"""
    datfiles = [x for x in files if x[-4:] == ".dat"]
    if len(datfiles) > 0:
        return datfiles[0][:-4]
    return None

def get_name_logfile(files):
    """this are the dat file"""
    datfiles = [x for x in files if x.find("_ref.log") != -1]
    #datfiles = [x for x in files if x.find("_tst.log") != -1]
    #datfiles = [x for x in files if x.find(".log") != -1]
    if len(datfiles) > 0:
        return datfiles[0]
    return None

def repair_names_logfile(start_dir):
    """walk through directory and correct names of logfiles"""
    for (path, dirs, files) in os.walk(start_dir):
        dat_name = get_name_datfile(files)
        #dat_name = os.path.basename(path)
        logfile_name = get_name_logfile(files)
        if dat_name is not None and logfile_name is not None:
            src = os.path.join(path, logfile_name)
            #new_name = logfile_name.replace("tst_ref.log", "tst_%s_ref.log" % dat_name)
            new_name = logfile_name.replace("_ref.log", "_reference.log")
            #new_name = "testrunner_tst_%s_reference.log" % dat_name
            dst = os.path.join(path, new_name)
            print(src, dst)
            os.rename(src, dst)

def repair_names_datfile(start_dir):
    """walk through directory and correct names of datfiles"""
    for (path, dirs, files) in os.walk(start_dir):
        dat_name = get_name_datfile(files)
        dir_name = os.path.basename(path)
        if dat_name is not None:
            src = os.path.join(path, dat_name) + '.dat'
            #new_name = logfile_name.replace("tst_ref.log", "tst_%s_ref.log" % dat_name)
            #new_name = logfile_name.replace("_tst.log", "_tst_%s_reference.log" % dat_name)
            new_name = "%s.dat" % dir_name
            dst = os.path.join(path, new_name)
            print(src, dst)
            os.rename(src, dst)         


def main():
    """main function"""
    start_dir = sys.argv[1]

    repair_names_logfile(start_dir)
    #repair_names_datfile(start_dir)

if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
