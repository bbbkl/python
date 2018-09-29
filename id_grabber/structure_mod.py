# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: structure_mod.py
#
# description
"""\n\n
    for given activiy ident_akt / part proc ids generate message.dat input
"""

import sys
import re
import os.path
from argparse import ArgumentParser

VERSION = '0.1'


id_offset = 0

def init_partproc_id(act_id, pp_id):
    """initialize id offset"""
    global id_offset
    id_offset = pp_id - act_id

def get_partproc_id(act_id):
    """get part proc id for given activity id"""
    global id_offset
    return act_id + id_offset

def aob_to_next_act(act_id, pbk_from='CAB', pbk_to='CAB', proc='VUA-00435132', aob=3):
    """
    print aob commands of act_id to next act_id to console
    PBK_FROM             CAB
    Prozess              VUA-00435132
    Teilprozess_FROM     1130735
    IdentAkt_FROM        1214559
    Teilprozess_TO       1130734
    IdentAkt_TO          1214558
    Transportzeit        0
    Transportzeiteinheit 0 (Sekunden)
    AOB                  3 (EA)
    Teillos              0
    Zeitwahl             OHNE
    MengeTeillos         1
    JeMengeTeillos       1
    PBK_TO               CAB
    """
    tokens = [3, pbk_from, proc, get_partproc_id(act_id), act_id, get_partproc_id(act_id+1), act_id+1, 0, 0, aob, 0, 'OHNE', 1, 1, pbk_to]
    tokens = [str(t) for t in tokens]
    print('\t'.join(tokens))
    print('2\t360\tDEF_ERPCommandcreate_Constraint___')

def strip_aobs(filename):
    """strip all AOBs out of geiven message filename"""
    new_file = filename[:-4] + "_aobs_stripped.dat"
    stream = open(new_file, "w")
    previous_line = None
    for line in open(filename):
        # 2    360    DEF_ERPCommandcreate_Constraint___
        if line.find('2\t360') == 0:
            previous_line = None
            continue
        if previous_line is not None:
            stream.write(previous_line)
        previous_line = line
    
    if previous_line is not None:
        stream.write(previous_line)
    stream.close()   

def matches_id(dataline, ids):
    """check whether one of the given ids occurs within dataline"""
    tokens = dataline.split('\t')
    for token in ids:
        if str(token) in tokens:
            return True
    return False

def strip_partprocs(filename, nostrip_ids):
    """strip partprocs except partprocs for given ids"""
    new_file = filename[:-4] + "_stripped_partprocs.dat"
    stream = open(new_file, "w")
    previous_line = None
    for line in open(filename):
        # 2    370    DEF_ERPCommandcreate_Process______
        if line.find('2\t370') == 0:
            if not matches_id(previous_line, nostrip_ids):
                previous_line = None
                continue
        if previous_line is not None:
            stream.write(previous_line)
        previous_line = line
    
    if previous_line is not None:
        stream.write(previous_line)
    stream.close()   
    
def is_altres(dataline):
    """return true if dataline contains altres info"""
    tokens = dataline.split('\t')
    return tokens[10] == '1'    
    
def strip_altres(filename):
    """strip partprocs except partprocs for given ids"""
    new_file = filename[:-4] + "_stripped_altres.dat"
    stream = open(new_file, "w")
    previous_line = None
    for line in open(filename):
        # 2    350    DEF_ERPCommandcreate_Resource_____
        if line.find('2\t350') == 0:
            if is_altres(previous_line):
                previous_line = None
                continue
        if previous_line is not None:
            stream.write(previous_line)
        previous_line = line
    
    if previous_line is not None:
        stream.write(previous_line)
    stream.close()       

def replace_partproc_ids(filename, id_from, id_to, id_new):
    """replace all ids 'from' to 'to' by given new id"""
    print("file: %s, from %d - to %d, replace by %d" % (filename, id_from, id_to, id_new))
    new_file = filename[:-4] + "_one_partproc.dat"
    stream = open(new_file, "w")
    for line in open(filename):
        tokens = line.split('\t')
        for i in range(0, len(tokens)):
            token = tokens[i]
            if token.isdigit():
                val = int(token)
                if id_from <= val and val <= id_to:
                    tokens[i] = str(id_new)
                    flag = 1
        new_line = '\t'.join(tokens)
        stream.write(new_line)
    stream.close() 
        
def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)

    
    parser.add_argument('lower_id', metavar='lower_id', help='lower activity ident_akt id')
    parser.add_argument('upper_id', metavar='upper_id', help='upper activity ident_akt id')
    parser.add_argument('upper_id_pp', metavar='upper_id_pp', help='upper partproc id')
    
    parser.add_argument('-a', '--strip_aobs', action="store_true", # or store_false
                      dest="strip_aobs", default=False, # negative store value
                      help="strip aobs out of given messagefile")
    
    parser.add_argument('--strip_altres', action="store_true", # or store_false
                      dest="strip_altres", default=False, # negative store value
                      help="strip altres group resources out of given messagefile")
    
    parser.add_argument('-pp', '--modify_partprocids', action="store_true", # or store_false
                      dest="mod_partproc_ids", default=False, # negative store value
                      help="modfy partproc ids within given message file, replace all partproc ids from-to by replace id")
    
    parser.add_argument('-sp', '--strip_partprocids', metavar='string',
                      dest='strip_partproc_ids', default='',
                      help='strip all partproc ids except given ones out of messagefile')
    
    parser.add_argument('-m', '--messagefile', metavar='string',
                      dest='messagefile', default='',
                      help='messagefile to handle')
    
    """
    parser.add_argument('-rid', '--res_id', metavar='string',
                      dest="res_id", default='',
                      help="grep process ids of processes which require given resource id")
    parser.add_argument('--fixed_ids', action="store_true", # or store_false
                      dest="fixed_ids", default=False, # negative store value
                      help="grep ids of completely fixed processes out of message_file")
    parser.add_argument('--partproc_duedate', action="store_true", # or store false)
                        dest='partproc_duedate', default=False, 
                        help="grep ids of processes which contain a partproc with own duedate")
    """

    return parser.parse_args()


def main():
    """main function"""
    args = parse_arguments()
    
    if args.strip_altres:
        strip_altres(args.messagefile)
        return
    
    if args.strip_partproc_ids:
        ids = args.strip_partproc_ids.split(',')
        strip_partprocs(args.messagefile, ids)
        return
    
    if args.strip_aobs:
        strip_aobs(args.messagefile)
        return
        
    lower_id = int(args.lower_id)
    upper_id = int(args.upper_id)
    upper_pp_id = int(args.upper_id_pp)

    if args.mod_partproc_ids: 
        replace_partproc_ids(args.messagefile, lower_id, upper_id, upper_pp_id)
        return

    #print("id1: %d, id2: %d, ppid2: %d" % (lower_id, upper_id, upper_pp_id))
    init_partproc_id(upper_id, upper_pp_id)
    #print("%d" % get_partproc_id(lower_id))

    
    for act_id in range(lower_id, upper_id):
        aob_to_next_act(act_id)


if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
