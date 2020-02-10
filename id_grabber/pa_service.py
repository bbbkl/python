# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: temp.py
#
# description
"""\n\n
    script to try something out and which is not lost after shutdown
"""

import re
import os.path
from argparse import ArgumentParser
import sys
from glob import glob

import win32con
import win32service
import win32serviceutil

VERSION = '0.1'

def join_files(dir_name):
    files = glob(dir_name + "/*.dat")
    out = open(os.path.join(dir_name, 'combined.dat'), 'w')
    for fn in files:
        print("handled %s" % fn)
        for line in open(fn):
            out.write(line)
        out.write('\n')
    out.close()


def walk_logfiles(startdir):
    for root, dirs, files in os.walk(startdir):
        for item in [x for x in files if os.path.splitext(x)[-1].lower() == '.log']:
            check_pairs(os.path.join(root, item))
            
def check_pairs(filename):
    rgx = re.compile(r'trace_id=(\d+)')
    rgx_thread = re.compile(r'thread_id=(\d+)')
    id_set = set()
    threads = set()
    for line in open(filename):
        hit = rgx.search(line)
        if hit:
            id = int(hit.group(1))
            if id in id_set:
                id_set.discard(id)
            else:
                id_set.add(id)
        hit = rgx_thread.search(line)
        if hit:
            threads.add(int(hit.group(1)))
    #if id_set:
    print("%s %s threads=%s" % (filename, id_set, threads))

def list_services():
    resume = 0
    accessSCM = win32con.GENERIC_READ
    accessSrv = win32service.SC_MANAGER_ALL_ACCESS

    #Open Service Control Manager
    hscm = win32service.OpenSCManager(None, None, accessSCM)

    #Enumerate Service Control Manager DB
    typeFilter = win32service.SERVICE_WIN32
    stateFilter = win32service.SERVICE_STATE_ALL

    statuses = win32service.EnumServicesStatus(hscm, typeFilter, stateFilter)

    #for (short_name, desc, status) in statuses: print(short_name, desc, status) 
    return statuses
    
def is_running(sv_status):
    return sv_status[1] == 4    
    
def delete_services(svc_id):
    for sv_name, sv_desc, sv_status in list_services():
        if sv_name.find(svc_id) != -1:
            try:
                print("delete service %s" % sv_name)
                
                svc_mgr = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS)
                svc_handle = win32service.OpenService(svc_mgr, sv_name, win32service.SERVICE_ALL_ACCESS)
                win32service.DeleteService(svc_handle)
                
            except:
                print("failed to delete service %s" % sv_name)  

def start_services(svc_id):
    for sv_name, sv_desc, sv_status in list_services():
        if sv_name.find('-dev-inwb') != -1 or (sv_name.find('APS-apsdemo')!=-1 and sv_name.find('apsdemo2')==-1):
            if svc_id == 'all' or sv_name.find(svc_id) != -1 and not is_running(sv_status):
                try:
                    print("start service %s" % sv_name)
                    
                    win32serviceutil.StartService(sv_name)
                    
                except:
                    print("failed to start service %s" % sv_name)  
                
def stop_services():
    for sv_name, sv_desc, sv_status in list_services():
        if sv_name.find('-dev-ftr') != -1 or sv_name.find('-apsdemo2') != -1:
            try:
                win32serviceutil.StopService(sv_name)
                print("stopped", sv_name)
            except:
                pass
    
def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('message_file', metavar='message_file', help='input message file')
    parser.add_argument('-d', '--del_svc', metavar='string', # or stare_false
                      dest="del_svc", default='', # negative store value
                      help="service to delete, e.g. 72c00")
    parser.add_argument('--start', metavar='string', # or stare_false
                      dest="start", default='', # negative store value
                      help="start services which match given version string, special version 'all'")
    """
    parser.add_argument('-m', '--mat-id', metavar='string', # or stare_false
                      dest="id_mat", default='', # negative store value
                      help="material id to grep")
    parser.add_argument('-c', '--count', metavar='N', type=int, # or stare_false
                      dest="count", default=0, # negative store value
                      help="count")
    parser.add_argument('-p', '--pattern', metavar='string', # or stare_false
                      dest="pattern", default='xxx', # negative store value
                      help="search pattern within logfile")
    """
    return parser.parse_args()        
        
def main():
    """main function"""
    args = parse_arguments()
    startdir = args.message_file
    
    #join_files(startdir)
    #walk_logfiles(startdir)
    if args.start:
        start_services(args.start)
        return
    
    if args.del_svc:
        delete_services(args.del_svc)
        return
    
    stop_services()



if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
