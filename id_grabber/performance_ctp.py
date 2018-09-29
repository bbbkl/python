# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: performance_ctp.py
#
# description
"""\n\n
    extract start and end times, job number, process id of single terminations as performance indicators. Write them to console.
"""

import sys
import re

def get_start_end_ctp_nr_52(filename):
    """get dict: job_id -> {start -> dateime, end ->datetime, ctp_id -> ctp_id}"""
    result = {}
    rgx_start  = re.compile(r'^(.*) TIME\:.*receive Order!')
    rgx_end    = re.compile(r'^(.*) TIME\:.*Send CTP.*Solution to ERP')
    rgx_ctp_nr = re.compile(r'calcCtp NR=(\d+)')
    rgx_job_nr = re.compile(r'current job number\:(\d+)')
 
    job_id = None
    info = {'start':"", 'end':"", 'ctp_id':""}

    for line in open(filename):
        hit = rgx_end.search(line)
        if hit:
            info['end'] = hit.group(1)
            if job_id is not None:
                result[job_id] = info.copy()
            info = {'start':"", 'end':"", 'ctp_id':""}
            job_id = None
        hit = rgx_start.search(line)
        if hit:
            info['start'] = hit.group(1)
        hit = rgx_ctp_nr.search(line)
        if hit:
            info['ctp_id'] = hit.group(1)
            job_id = int(hit.group(1))

    return result

def get_start_end_ctp_nr(filename):
    """get dict: job_id -> {start -> dateime, end ->datetime, ctp_id -> ctp_id}"""
    result = {}
    rgx_start  = re.compile(r'^(.*) TIME\:.*receive Order!') #re.compile(r'^(.*) TIME\:.*setJobContextCTP')
    rgx_end    = re.compile(r'^(.*) TIME\:.*Sent CTP.*Solution to ERP')
    rgx_ctp_nr = re.compile(r'calcCtp NR=(\d+)')
    rgx_job_nr = re.compile(r'current job number\:(\d+)')
 
    job_id = None
    info = {'start':"", 'end':"", 'ctp_id':""}

    for line in open(filename):
        hit = rgx_end.search(line)
        if hit:
            info['end'] = hit.group(1)
            if job_id is not None:
                result[job_id] = info.copy()
            info = {'start':"", 'end':"", 'ctp_id':""}
            job_id = None
        hit = rgx_start.search(line)
        if hit:
            info['start'] = hit.group(1)
        hit = rgx_ctp_nr.search(line)
        if hit:
            info['ctp_id'] = hit.group(1)
        hit = rgx_job_nr.search(line)
        if hit:
            job_id = hit.group(1)

    return result

def get_start_times(filename):
    """get dict job_id -> datetime e.g. 699848 -> 29.09.2014 10:12:34"""
    result = {}
    # rgx_start = re.compile(r'^(.*) TIME\:.*JobNr\: (\d+).*CreateTempStarted ERP')
    rgx_start = re.compile(r'^(.*) TIME\:.*setJobContextCTP, job id\: (\d+)')
    for line in open(filename):
        hit = rgx_start.search(line)
        if hit:
            time_str, job_id = hit.groups()
            result[job_id] = time_str
    return result

def get_end_times(filename):
    """get dict job_id -> datetime e.g. 699848 -> 29.09.2014 10:12:34"""
    result = {}
    #rgx_end = re.compile(r'^(.*) TIME\:.*JobNr\: (\d+).*ResultReceived LST')
    rgx_end = re.compile(r'^(.*) TIME\:.*Sent CTP.*Solution to ERP, job id\: (\d+)')
    for line in open(filename):
        hit = rgx_end.search(line)
        if hit:
            time_str, job_id = hit.groups()
            result[job_id] = time_str
    return result

def get_ctp_nr(filename):
    """get dict job_id -> ctp number"""
    result = {}
    rgx_ctp_nr = re.compile(r'calcCtp NR=(\d+)')
    rgx_job_nr = re.compile(r'current job number\:(\d+)')
    ctp_nr = None
    for line in open(filename):
        if ctp_nr is not None:
            hit = rgx_job_nr.search(line)
            if hit:
                result[hit.group(1)] = ctp_nr
                ctp_nr = None
        hit = rgx_ctp_nr.search(line)
        if hit:
            ctp_nr = hit.group(1)
    return result

def main():
    """main function"""
    filename = sys.argv[1]

    if 0: # new style
        start_times = get_start_times(filename)
        end_times   = get_end_times(filename)
        ctp_numbers = get_ctp_nr(filename)

        for job_id in sorted(start_times):
            start_time = start_times[job_id]
            end_time = end_times[job_id] if job_id in end_times else ''
            ctp_nr = ctp_numbers[job_id] if job_id in ctp_numbers else ''
            print('%s;%s;%s;%s' % (job_id, ctp_nr, start_time, end_time))

    else:
        infos = get_start_end_ctp_nr_52(filename)
        for job_id in sorted(infos):
            info = infos[job_id]
            start_time = info['start']
            end_time = info['end']
            ctp_nr = info['ctp_id']
            print('%s;%s;%s;%s' % (job_id, ctp_nr, start_time, end_time))


if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
