# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: get_creation_date_csv.py
#
# description
"""\n\n
    for a given message file get all head processes and write a csv file
    containing the prio, today, due_date, creation_date
"""

import sys
import time
import re


def get_creation_date(prio, due_date, today):
    """(due_date + today - xval) / 2 = creation_date"""
    truncated_prio = (float(prio) * 10 - int(float(prio) * 10)) / 10
    xval = float(truncated_prio) * 1000000
    if xval == 0:
        return "NN"

    one_day     = 60 * 60 * 24.0 # in seconds
    date_format = "%d.%m.%Y"
    due_date    = time.mktime(time.strptime(due_date, date_format)) / one_day
    today       = time.mktime(time.strptime(today, date_format)) / one_day

    ad_secs = one_day * (due_date + today - xval) / 2.0 + one_day

    return time.strftime(date_format, time.gmtime(ad_secs))

def tokenize(dataline):
    """split dataline into tokens"""
    return dataline[:-1].split('\t')

def get_server_date(filename):
    """open file, parse until server date is found, return it"""
    dataline = None
    for line in open(filename):
        if re.search(r'^3\t', line):
            dataline = line
        if re.search(r'^2\t150', line): # ServerInfo
            if dataline:
                return tokenize(dataline)[1]
    raise Exception("failed to get server date")

def get_process_lines(filename):
    """open file, parse for tr process lines, return them"""
    result = []
    dataline = None
    for line in open(filename):
        if re.search(r'^3\t', line):
            dataline = line
        if re.search(r'^2\t370', line): # DEF_ERPCommandcreate_Process______
            if dataline:
                result.append(dataline)
    return result

def filter_head_processes(process_lines):
    """filter non head process lines out of all process line"""
    return [x for x in process_lines if tokenize(x)[17] == '1']

def get_due_date(process_line):
    """due date"""
    return tokenize(process_line)[9]

def get_priority(process_line):
    """priority with '.' as floating point indicator"""
    return tokenize(process_line)[11].replace(',', '.')

def get_pid(process_line):
    """process id"""
    return tokenize(process_line)[2]

def get_rmnr(process_line):
    """rueckmeldenummer"""
    return tokenize(process_line)[3]

def get_short_prio(prio):
    """get real priority part without encoded age/due date stuff"""
    return int(10 * float(prio))

def get_ordered_priorities(process_lines):
    """return oredered list of process priorities"""
    items = [get_priority(x) for x in process_lines]
    items.sort()
    items.reverse()
    return items


def print_csv_file_to_console(filename):
    """parse a message file, calculate creation date for each process and write data to console"""
    server_date = get_server_date(filename)
    process_lines = get_process_lines(filename)
    process_lines = filter_head_processes(process_lines)

    ordered_priorities = get_ordered_priorities(process_lines)

    print('process;rmnr;today;prio_long;position;prio;creation_date;due_date')
    for line in process_lines:
        prio          = get_priority(line)
        due_date      = get_due_date(line)
        creation_date = get_creation_date(prio, due_date, server_date)

        short_prio    = get_short_prio(prio)
        pos           = ordered_priorities.index(prio)
        prio          = str(prio).replace('.', ',')

        print("'%s';%s;%s;%s;%d;%d;%s;%s" % (get_pid(line), get_rmnr(line), server_date, prio, pos, short_prio, creation_date, due_date))

def main():
    """main function"""
    filename = sys.argv[1]

    print_csv_file_to_console(filename)



if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
