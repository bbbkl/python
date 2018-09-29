# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: statistic_dispobeweg.py
#
# description
"""\n\n
    take messagefile. Parse all DEF_ERPCommandcreate_M_DispoBew___ entries.
    Use field schluessel_herkunft an generate statistic for different prefixes.
"""

import os
import re
from argparse import ArgumentParser

VERSION = '0.1'

def parse_dispo_beweg_entries(message_file):
    """parse all dispo beweg entries out of given message file"""
    result = []
    dataline = None
    
    for line in open(message_file):
        if re.search(r'^2\t301', line): # DEF_ERPCommandcreate_M_DispoBew___
            try:
                tokens = tokenize(dataline)
            except:
                print("line was '%s'" % line)
                raise
            
            result.append(tokens[1:])
            
        elif re.search(r'^2\t(120|196)', line): # Sync/Opti end
            break
        
        else:
            dataline = line
    
    return result

def parse_dispo_beweg_belegart(message_file):
    """parse all dispo beweg entries out of given message file"""
    result = []
    dataline = None
    
    for line in open(message_file):
        if re.search(r'^2\t301', line): # DEF_ERPCommandcreate_M_DispoBew___
            try:
                tokens = tokenize(dataline)
            except:
                print("line was '%s'" % line)
                raise
            
            result.append(tokens[7])
            
        elif re.search(r'^2\t(120|196)', line): # Sync/Opti end
            break
        
        else:
            dataline = line
    
    return result
        
def parse_messagedate(message_file):
    """parse date out of given messsagefile"""
    dataline = None
    for line in open(message_file):
        if re.search(r'^2\t150', line): # DEF_ERPCommandsetServer___________
            try:
                tokens = tokenize(dataline)
            except:
                print("line was '%s'" % line)
                raise
            date = tokens[1]
            time = tokens[2]
            return "%s %s" % (date, time)
        else:
            dataline = line
            
    return "NN"
                
        
def get_header():     
    """show header entries"""
    return ['message_id', 'datetime', 
            'ArtId', 'part_variant', 'Dispotermin', 'demand_quantity', 'Deckungsmenge',
            'Reservierungsmenge', 'Belegart_herkunft', 'Schl_herkunft', 'Dispozeit',
            'cro', 'mrp_area', 'lot', 'Active_order']
    pass

def show_statistic(entries):
    """create statistic for given schuessel_herkunft entries, print to console"""
    stat = {}
    for belegart, schluessel in entries:
        stat.setdefault(belegart, 0)
        stat[belegart] += 1
    
    print("total: %d (100%)")
    total = len(entries)
    for key in stat.keys():
        pct = stat[key] * 100.0 / total
        print("\t%s %d %f" )
        
    for entry in entries:
        print("entry: %s" % entry)

def tokenize(dataline):
    """split dataline into tokens"""
    if dataline.find('1\t')==0:
        dataline = dataline[2:]
    if dataline[-1] == '\n':
        dataline = dataline[:-1]
    return dataline.split('\t')

def write_to_output(message_file, datetime, entries, output_file):
    """append to output file"""
    stream = open(output_file, "a")
    if os.path.getsize(output_file) == 0:
        stream.write("%s\n" % ';'.join(get_header()))
    
    for items in entries:
        stream.write("%s;%s;%s\n" % (message_file, datetime, ';'.join(items)))
    stream.close()
    
def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file> <output csv file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('output_file', metavar='output_file', help='output file')
    parser.add_argument('message_files', nargs='+', help='<Required> 1 to n message files')
    return parser.parse_args()

def main():
    """main function"""
    args = parse_arguments()
    message_files = args.message_files
    output_file = args.output_file
   
    for message_file in message_files:
        if 1:
            print("handle %s ..." % message_file)
            datetime = parse_messagedate(message_file) 
            entries = parse_dispo_beweg_entries(message_file)
            write_to_output(message_file, datetime, entries, output_file)
        if 0:
            items = parse_dispo_beweg_belegart(message_file)
            print("%s" % message_file)
            
if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise