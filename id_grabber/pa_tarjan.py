# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: pa_tarjan.py
#
# description
# for given TT_M_DispoOrderSuccessor.json calculate cycles with tarjan algo
from pickle import NONE
from tarjan import tarjan, strip_result


"""\n\n
    script to try something out and which is not lost after shutdown
"""
import re
from argparse import ArgumentParser
import os.path
import shutil
from subprocess import run, PIPE
from glob import glob

VERSION = '0.1'


def parse_successor_infos(input_file):
    rgx_part = re.compile('Artikel".*"([^"]*)"')
    rgx_var = re.compile('ArtVar".*"([^"]*)"')
    rgx_mrparea = re.compile('MRPArea"[^0-9]+(\d+)')
    rgx_part_s = re.compile('ArtikelSuccessor".*"([^"]*)"')
    rgx_var_s = re.compile('ArtikelVarSuccessor.*"([^"]*)"')
    rgx_mrparea_s = re.compile('MRPAreaSuccessor[^0-9]+(\d+)')
    
    successors = {}
    
    part = var = mrp = part_s = var_s = mrp_s = NONE
    for line in open(input_file):
        hit = rgx_part.search(line)
        if hit:
            part = hit.group(1)
            continue
        hit = rgx_var.search(line)
        if hit:
            var = hit.group(1)
            continue
        hit = rgx_mrparea.search(line)
        if hit:
            mrp = hit.group(1)
            continue
        hit = rgx_part_s.search(line)
        if hit:
            part_s = hit.group(1)
            continue
        hit = rgx_var_s.search(line)
        if hit:
            var_s = hit.group(1)
            continue
        hit = rgx_mrparea_s.search(line)
        if hit:
            mrp_s = hit.group(1)
            v = "/" + var if var else ""
            vs = "/" + var_s if var_s else ""
            
            a = "%s%s/%s" % (part,v,mrp)
            b = "%s%s/%s" % (part_s,vs,mrp_s)
            successors.setdefault(a, [])
            successors[a].append(b)
    
    for key in successors:
        print("%s -> %s" % (key, successors[key]))
    print()
    for key in successors:
        if key in successors[key]:
            print("direct circle %s <-> %s" % (key, key))
    print(strip_result(tarjan(successors)))
            

def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('jason_tt_file', metavar='jason_tt_file', help='jason dump to temp table TT_M_DispoOrderSuccessor')

    
    return parser.parse_args()

def main():
    """main function"""
    args = parse_arguments()

    parse_successor_infos(args.jason_tt_file)
    
    
if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
