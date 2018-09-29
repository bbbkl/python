# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: what_problem.py
#
# description
"""\n\n
    for a given message file read information of first contained full optimization or synchronization
    and write problem statistics to console.
    
    If there are multiple messagefiles available, read all of them and write header information in first line.
"""

import os
import re
from argparse import ArgumentParser
from cluster_cp import get_consumer_producer_info, calculate_dispolevel

VERSION = '0.1'

cmd_activity   = 365
cmd_process    = 370
cmd_material   = 325
cmd_resource   = 311
cmd_mat_cst    = 355
cmd_res_cst    = 350
cmd_set_server = 150
cmd_opti       = 120
cmd_sync       = 196

def special_commands():
    """treat these commands special"""
    return set([cmd_activity, cmd_process, cmd_mat_cst, cmd_res_cst])

def get_max_dispolevel(message_file):
    """calculate dispolevel, return max calculated level"""
    cp_infos = get_consumer_producer_info(message_file)
    calculate_dispolevel(cp_infos)
    max_level = 0
    for proc_id in cp_infos:
        dispolevel = cp_infos[proc_id]['dispolevel']
        if dispolevel > max_level:
            max_level = dispolevel
    return max_level

def get_maximums(proc_dict):
    """show max values for each command"""
    special = special_commands()
    max_dict = {}
    for cmd in special:
        max_dict[cmd] = 0
        max_dict[str(cmd)] = ''
    for proc_id in proc_dict:
        detail_dict = proc_dict[proc_id]
        for cmd in detail_dict:
            if max_dict[cmd] < detail_dict[cmd]:
                max_dict[cmd] = detail_dict[cmd]
                max_dict[str(cmd)] = proc_id
    return max_dict

def get_max_multres(act_to_res_dict):
    """get max multires usage"""
    if 0:
        max_val = max(act_to_res_dict.values())
        for ident_act in act_to_res_dict:
            if act_to_res_dict[ident_act] == max_val:
                print("identact: %s -> %d" % (ident_act, max_val) )
    return max(act_to_res_dict.values())

def print_header():
    """print header to console"""
    print(";".join(get_header_items()))

def get_header_items():
    """get header items"""
    header_items = [
        'id',
        'date', 
        '#Aufträge',
        '#Baugruppen',
        '#Aktivitäten',
        '#Teile',
        '#Ressourcen',
        '#Bedarfe',
        '#Ressourcen-Zuordnungen',
        'max Baugruppen',
        'max Aktivitäten',
        'max Bedarfe',
        'max Ressourcen-Zuordnungen',
        'max Multiressource',
        'max Dispostufe' ]
    
    return header_items
              
              

def get_value(mapping, key):
    """return mapping entry for key, if any, 0 otherwise"""
    if key in mapping: 
        return mapping[key]
    return 0

def print_stats(message_id, message_date, cmd_dict, max_dict, max_multires, \
                max_dispolevel, with_colnames):
    """print statistics to console"""
    
    values = []
    
    values.append(message_id)
    values.append(message_date)
    
    values.append(get_value(cmd_dict, 'headproc'))
    values.append(get_value(cmd_dict, cmd_process))
    values.append(get_value(cmd_dict, cmd_activity))
    values.append(get_value(cmd_dict, cmd_material))
    values.append(get_value(cmd_dict, cmd_resource))
    values.append(get_value(cmd_dict, cmd_mat_cst))
    values.append(get_value(cmd_dict, cmd_res_cst))
    
    values.append(get_value(max_dict, cmd_process))
    values.append(get_value(max_dict, cmd_activity))
    values.append(get_value(max_dict, cmd_mat_cst))
    values.append(get_value(max_dict, cmd_res_cst))
    
    values.append(max_multires)
    values.append(max_dispolevel)
   
    csv_line = "%s" % values[0]
    for value in values[1:]:
        csv_line += ';%s' % value
   
    if with_colnames:
        header_items = get_header_items()
        max_len = max([len(x) for x in  header_items]) + 1
        fmt = '%%-%ds %%s' % max_len
        result = fmt % (header_items[0] + ':', values[0])
        for i in range(1, len(values)):
            result += '\n' + fmt % (header_items[i] + ':', values[i])
        print(result)
        print()
   
    print(csv_line)
    
def get_proc_id(dataline, command):
    """get process id out of given dataline with respect to corresponding command"""    
    try:
        tokens = tokenize(dataline)
    except:
        print("line was '%s'" % dataline)
        raise
    if command==cmd_activity:
        return tokens[1]
    if command==cmd_process:
        return tokens[1]
    if command==cmd_mat_cst:
        return tokens[1]
    if command==cmd_res_cst:
        return tokens[1]
    raise "get_proc_id, unhandled command %d" % command

def is_headproc(dataline):
    """get head proc info out of given dataline which belongs to a create_process command"""
    return tokenize(dataline)[16]=='1'

def get_act_id(dataline, command):
    """get activity id of given dataline with respect to corresponding command"""
    try:
        tokens = tokenize(dataline)
    except:
        print("line was '%s'" % dataline)
        raise   
    if command==cmd_res_cst:
        return tokens[7]
    raise "get_act_id, unhandled command %d" % command
    
def enrich_stats(dataline, command, proc_dict):
    """enrich statistcs"""
    proc_id = get_proc_id(dataline, command)
    #print("proc_id=%s, line='%s'" % (proc_id, dataline))
    proc_dict.setdefault(proc_id, {})
    detail_dict = proc_dict[proc_id]
    detail_dict.setdefault(command, 0)
    detail_dict[command] += 1

def enrich_multres(dataline, act_to_res_dict):
    """enrich multi resrouce info"""
    act_id = get_act_id(dataline, cmd_res_cst)
    act_to_res_dict.setdefault(act_id, 0)
    act_to_res_dict[act_id] += 1

def tokenize(dataline):
    """split dataline into tokens"""
    if dataline.find('1\t')==0:
        dataline = dataline[2:]
    if dataline[-1] == '\n':
        dataline = dataline[:-1]
    return dataline.split('\t')

def parse_message_file(message_file, with_colnames=False):
    special = special_commands()
    dataline = None
    cmd_dict = {}
    proc_dict = {}
    act_to_res_dict = {}
    message_date = ''
    end_token_hit = False
    
    rgxDataline = re.compile(r'^3\t(.*)')
    rgxCommandline = re.compile(r'^2\t(\d+)')
    for line in open(message_file):
        hit = rgxDataline.search(line)
        if hit:
            dataline = hit.group(1)
            continue
        hit = rgxCommandline.search(line)
        if not hit:
            continue
        command = int(hit.group(1))
        cmd_dict.setdefault(command, 0)
        cmd_dict[command] += 1
        if command in (cmd_opti, cmd_sync):
            end_token_hit = True
            break
        if command in special:
            enrich_stats(dataline, command, proc_dict)
        if command == cmd_res_cst:
            enrich_multres(dataline, act_to_res_dict)
        if command == cmd_set_server:
            message_date = tokenize(dataline)[0]
        # use dedicated dict/set for headprocs?
        if command == cmd_process and is_headproc(dataline):
            cmd_dict.setdefault('headproc', 0)
            cmd_dict['headproc'] += 1
        
    if not end_token_hit:
        return # skip files with no end_of_sync / end_of_opti command
    #print("commands: %s" % cmd_dict )
    #print("stats: %s" % proc_dict)
    
    message_id = os.path.basename(message_file)
    max_dispolevel = get_max_dispolevel(message_file)
    print_stats(message_id, message_date, cmd_dict, get_maximums(proc_dict), \
                get_max_multres(act_to_res_dict), max_dispolevel, with_colnames)

def walk_messages(start_dir):
    """go recursively through filesystem and process each messagefile"""
    print_header()
    for dir, dirnames, filenames in os.walk(start_dir):
        messagefiles = filter (lambda x: x[-4:].lower()=='.dat', filenames)
        for mf in messagefiles:
            message_file = os.path.join(dir, mf)
            parse_message_file(message_file)

def parse_arguments():
    """parse arguments from command line"""
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('message_file', metavar='message_file', help='input message_file')
    return parser.parse_args()

def main():
    """main function"""
    args = parse_arguments()
    arg0 = args.message_file
    
    if os.path.isdir(arg0):
        walk_messages(arg0)
    else:
        message_file = arg0
        parse_message_file(message_file, True)

if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
