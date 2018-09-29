# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: id_grabber.py
#
# description
"""\n\n
    modify md_artikel lines (preproduction_data_relevant, dynamic_replenishment_time)
"""

import sys
import re
import os.path
from argparse import ArgumentParser

VERSION = '0.1'

def tokenize(dataline):
    return dataline.split('\t')

def modify_dynamic_replenishment_time(filename, new_value):
    tmp_file = filename + ".tmp"
    stream = open(tmp_file, "w")
    
    dataline = None
    counterlines = []
    for line in open(filename):
        if line.find('2\t335') == 0: # DEF_ERPCommandcreate_MD_Artikel___
            if dataline != None:
                tokens = tokenize(dataline)
                if len(tokens)>=18:
                    tokens[-2] = new_value
                    dataline = '\t'.join(tokens)
        
        if line.find('4\t') == 0:
            counterlines.append(line)
            continue
        
        if line.find('3\t') == 0:
            if dataline is not None:
                stream.write(dataline)
            if counterlines is not None:
                for item in counterlines:
                    stream.write(item)
                counterlines = []
            dataline = line
            continue
    
        if dataline is not None:
            stream.write(dataline)
            dataline = None
        if counterlines is not None:
            for item in counterlines:
                stream.write(item)
            counterlines = []
        stream.write(line)
    
    if dataline is not None:
        stream.write(dataline)
    if counterlines is not None:
        for item in counterlines:
            stream.write(item)    
    
    stream.close()
    
    tmp_file2 = filename + ".tmp2"
    os.rename(filename, tmp_file2)
    os.rename(tmp_file, filename)
    os.remove(tmp_file2)
    
    
def modify_advance_coverages(filename, new_value):
    tmp_file = filename + ".tmp"
    stream = open(tmp_file, "w")
    
    dataline = None
    counterlines = []
    for line in open(filename):
        if line.find('2\t335') == 0: # DEF_ERPCommandcreate_MD_Artikel___
            if dataline != None:
                tokens = tokenize(dataline)
                if len(tokens)>=18:
                    tokens[-1] = new_value + '\n'
                    dataline = '\t'.join(tokens)
        
        if line.find('4\t') == 0:
            counterlines.append(line)
            continue
        
        if line.find('3\t') == 0:
            if dataline is not None:
                stream.write(dataline)
            if counterlines is not None:
                for item in counterlines:
                    stream.write(item)
                counterlines = []
            dataline = line
            continue
    
        if dataline is not None:
            stream.write(dataline)
            dataline = None
        if counterlines is not None:
            for item in counterlines:
                stream.write(item)
            counterlines = []
        stream.write(line)
    
    if dataline is not None:
        stream.write(dataline)
    if counterlines is not None:
        for item in counterlines:
            stream.write(item)    
    
    stream.close()
    
    tmp_file2 = filename + ".tmp2"
    os.rename(filename, tmp_file2)
    os.rename(tmp_file, filename)
    os.remove(tmp_file2)    

def find_preproduction_date_relevant(start_dir):
    """find all *.dat files which still contain preproduction_date_relevant"""
    for (path, dirs, files) in os.walk(start_dir):
        src_files = [x for x in files if os.path.splitext(x)[-1] in ['.dat',]]
        for src_file in src_files:
            strip_preproduction_date_relevant(os.path.join(path, src_file))
            
def strip_preproduction_date_relevant(filename):
    tmp_file = filename + ".tmp"
    stream = open(tmp_file, "w")
    
    dataline = None
    counterlines = []
    for line in open(filename):
        if line.find('2\t335') == 0: # DEF_ERPCommandcreate_MD_Artikel___
            if dataline != None:
                tokens = tokenize(dataline)
                if len(tokens)==19:
                    del(tokens[-3])
                    dataline = '\t'.join(tokens)
        
        if line.find('4\t') == 0:
            counterlines.append(line)
            continue
        
        if line.find('3\t') == 0:
            if dataline is not None:
                stream.write(dataline)
            if counterlines is not None:
                for item in counterlines:
                    stream.write(item)
                counterlines = []
            dataline = line
            continue
 
        if dataline is not None:
            stream.write(dataline)
            dataline = None
        if counterlines is not None:
            for item in counterlines:
                stream.write(item)
            counterlines = []
        stream.write(line)
    
    if dataline is not None:
        stream.write(dataline)
    if counterlines is not None:
        for item in counterlines:
            stream.write(item)  
    
    stream.close()
    
    tmp_file2 = filename + ".tmp2"
    os.rename(filename, tmp_file2)
    os.rename(tmp_file, filename)
    os.remove(tmp_file2)

def replace_yes_no(filename):
    """replace YES/NO by 1/0""" 
    tmp_file = filename + ".tmp"
    stream = open(tmp_file, "w")
    
    dataline = None
    counterlines = []
    for line in open(filename):
        if line.find('2\t335') == 0 or line.find('2\t334') == 0 or line.find('2\t301') == 0:
            if dataline != None:
                tokens = tokenize(dataline)
                for idx, token in enumerate(tokens):
                    #print(token)
                    if token.find('NO')==0:
                        tokens[idx] = token.replace('NO', '0') 
                    if token.find('YES')==0:
                        tokens[idx] = token.replace('YES', '1') 
                dataline = '\t'.join(tokens)
        
        if line.find('4\t') == 0:
            counterlines.append(line)
            continue
        
        if line.find('3\t') == 0:
            if dataline is not None:
                stream.write(dataline)
            if counterlines is not None:
                for item in counterlines:
                    stream.write(item)
                counterlines = []
            dataline = line
            continue
 
        if dataline is not None:
            stream.write(dataline)
            dataline = None
        if counterlines is not None:
            for item in counterlines:
                stream.write(item)
            counterlines = []
        stream.write(line)
    
    if dataline is not None:
        stream.write(dataline)
    if counterlines is not None:
        for item in counterlines:
            stream.write(item)  
    
    stream.close()
    
    tmp_file2 = filename + ".tmp2"
    os.rename(filename, tmp_file2)
    os.rename(tmp_file, filename)
    os.remove(tmp_file2)

def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)

    parser.add_argument('message_file', metavar='message_file', help='input message file')
    parser.add_argument('-s', '--strip_preprodution_date_relevant', action="store_true",
                      dest="strip_preprodution_date_relevant", default=False,
                      help="strip preproduction_date_relevant out of md_artikel data")
    
    parser.add_argument('-d', '--dynamic_replenishment_time', metavar='integer',
                      dest="dynamic_replenishment_time", default=2,
                      help="dynamic_replenishment_time 2: do nth, 1: all 1, 0: all 0")
    
    parser.add_argument('-a', '--advance_coverages', metavar='integer',
                      dest="advance_coverages", default=2,
                      help="advance_coverages 2: do nth, 1: all 1, 0: all 0")
    
    parser.add_argument('-y', '--yes_no_replace', action="store_true",
                      dest="yes_no", default=False,
                      help="replace YES or NO in data of some commands to 1/0")
    
    parser.add_argument('-p', '--find_preproductiondaterelevant', action="store_true",
                      dest="find_preproduction_date_relevant", default=False,
                      help="find preproductiondate relevant files")

    return parser.parse_args()

def main():
    """main function"""
    args = parse_arguments()
    filename = args.message_file

    if args.find_preproduction_date_relevant:
        find_preproduction_date_relevant(filename)
        return

    if args.strip_preprodution_date_relevant:
        strip_preproduction_date_relevant(filename)
    
    if args.dynamic_replenishment_time != 2:
        print("dynamic_replenishment_time=%s" % args.dynamic_replenishment_time)
        modify_dynamic_replenishment_time(filename, args.dynamic_replenishment_time)
        
    if args.advance_coverages != 2:
        print("advance_coverages=%s" % args.advance_coverages)
        modify_advance_coverages(filename, args.advance_coverages)
        
    if args.yes_no:
        replace_yes_no(filename)


if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
