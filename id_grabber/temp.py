# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: temp.py
#
# description

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

def convert_dotfiles(dotfile_dir):
    dotfiles = []
    for fn in glob(dotfile_dir + "/*.dot"):
        if fn[-4:] != ".dot":
            continue
        if os.path.exists(fn + ".svg"):
            continue
        dotfiles.append(fn)
    
    for dot_file in dotfiles:
        call_graphviz(dot_file)
        print("handled %s" % dot_file)

def call_graphviz(dot_file):
    """call graphviz for given dotfile"""
    exe = r"C:\Program Files (x86)\Graphviz2.38\bin\dot.exe"
    params = "-Gcharset=latin1 -Tsvg -o%s.svg %s" % (dot_file, dot_file)        
    cmd = '%s %s' % (exe, params)
    run(cmd) #, stdout=outstream, stderr=outstream)
    
def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('message_file', metavar='message_file', help='input message file')

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

    convert_dotfiles(args.message_file)
    
    
if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
