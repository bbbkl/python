# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: pa_fh_wien.py
#
# description
"""\n\n
    script to deplay/copy/provide n aps users
"""

import re
from argparse import ArgumentParser
import shutil
import os
import subprocess


VERSION = '0.1'

def parse_licfile(lic_file):
    rgx = re.compile(r'<CompanyID>(.+)</CompanyID>')
    num2id = {}
    with open(lic_file) as istream:
        for line in istream:
            hit = rgx.search(line)
            if hit:
                id = hit.group(1)
                num2id[int(id)] = id
    for key in sorted(num2id.keys()):
        print(num2id[key])

def get_aps_id(base_id):
    """change aps prefix here, if lowercase or uppercase version is wanted"""
    aps_prefix = "APS"
    return aps_prefix + base_id

def get_aps_ids(ids_file):
    result = []
    with open(ids_file) as istream:
        for line in istream:
            id = line.strip()
            if id:
                result.append(get_aps_id(id))
    return result

def make_dirs(src_dir, dst_names):
    if not os.path.exists(src_dir):
        raise "no such sample dir '%s'" % src_dir
    base_dir = os.path.dirname(src_dir)
    for dst_name in dst_names:
        dst_dir = os.path.join(base_dir, dst_name)
        if os.path.exists((dst_dir)):
            continue
        print("create %s" % dst_dir)
        shutil.copytree(src_dir, dst_dir)

def report_sonic_queue_names(aps_ids):
    for aps_id in aps_ids:
        print("apsMessaging..%s.fromApsServer" % aps_id)
        print("apsMessaging..%s.toApsServer" % aps_id)

def get_service_name(aps_id):
    # pa-at-9-production-APS-aps1
    return "pa-at-9-production-APS-" + aps_id

def get_base_dir():
    return r'E:/proalpha/pa-at-9/production/runtime/opt'

def get_host_and_port():
    return r'PADATA-PROD-N1:12078'

def get_bin_path(aps_id):
    pth = os.path.join(get_base_dir(), aps_id, 'optsrv64.exe')
    if pth.find(' '):
        pth = '"%s"' % pth
    return pth

def get_logfile_name(aps_id):
    return r'E:\proalpha\pa-at-9\production\log\opt\%s\opt-production-%s.log' % (aps_id, aps_id)

def get_service_binpath(aps_id):
    res = '%s -servie' % get_bin_path(aps_id)
    res += ' -b tcp://%s' % get_host_and_port()
    res += ' -s %s' % aps_id
    res += ' -ServiceName %s' % get_service_name(aps_id)
    res += ' -l %s' % get_logfile_name(aps_id)
    res += ' -w %s' % os.path.join(get_base_dir(), aps_id)
    res += ' -u Administrator -p Administrator'
    return res

def get_service_args(aps_id):
    args = []
    args.append('sc.exe')
    args.append('create')
    args.append(get_service_name(aps_id))
    args.append('binpath=%s' % get_service_binpath(aps_id))
    return args

def create_services(aps_ids):
    for aps_id in aps_ids:
        subprocess.run(get_service_args(aps_id))

def delete_services(aps_ids):
    for aps_id in aps_ids:
        args = ['sc.exe', 'delete', get_service_name(aps_id)]
        subprocess.run(args)

def install_service(aps_id):
    name = get_service_name(aps_id)
    exe = os.path.join(get_base_dir(), 'optsrv64.exe')


def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('ids_file', metavar='ids_file', help='input file with subsystem ids without aps prefix')
    parser.add_argument('-mkdir', '--make_aps_dirs', metavar='string',
                        dest="mkdir", default='',
                        help="for given sample dir, create for each id in ids_file a copy")
    parser.add_argument('-cid', '--create_id_textfile', metavar='string',
                        dest="create_ids", default='',
                        help="for given lic file, print contained ids to console")
    parser.add_argument('-s', '--sonic_queue_name', action="store_true",  # or stare_false
                        dest="sonic_qnames", default=False,  # negative store value
                        help="print required sonic queue names to console")
    parser.add_argument('-sc', '--service_create', action="store_true",  # or stare_false
                        dest="service_create", default=False,  # negative store value
                        help="create services for all ids with id file")
    parser.add_argument('-sd', '--service_delete', action="store_true",  # or stare_false
                        dest="service_delete", default=False,  # negative store value
                        help="delete services for all ids with id file")
    return parser.parse_args()

def main():
    """main function"""
    args = parse_arguments()

    if args.create_ids:
        parse_licfile(args.create_ids)
        return
    if args.mkdir:
        aps_ids = get_aps_ids(args.ids_file)
        make_dirs(args.mkdir, aps_ids)
        return
    if args.sonic_qnames:
        aps_ids = get_aps_ids(args.ids_file)
        report_sonic_queue_names(aps_ids)
        return
    if args.service_create:
        aps_ids = get_aps_ids(args.ids_file)
        create_services(aps_ids)
        return
    if args.service_delete:
        aps_ids = get_aps_ids(args.ids_file)
        delete_services(aps_ids)
        return
    
if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
