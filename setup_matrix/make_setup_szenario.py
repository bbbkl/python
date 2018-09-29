# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: process_template.py
#
# description
"""\n\n
    process template for setup matrix
"""

from argparse import ArgumentParser
from setup_matrix.setup_util import test_encoding
from setup_matrix.process_template import parse_process_template#, ProcessTemplate
from copy import deepcopy

VERSION = '0.1'

def prepare_messagefile(filename, procs_to_insert):
    encoding_id = test_encoding(filename)
    out = open(filename.replace('.dat', '.szenario.dat'), 'w', encoding=encoding_id)
    before_cmd_183 = True # 183=DEF_ERPCommandsend_alle_Auftraege_
    found_cmd_103 = False # 103=DEF_ERPCommandERPTransferComplete_
    for line in open(filename, encoding=encoding_id):
        if before_cmd_183 or found_cmd_103:
            out.write(line)
        if line.find('2\t183')==0:
            before_cmd_183=False
            out.write(procs_to_insert)
        if not before_cmd_183 and line.find('2\t103')==0:
            out.write(line)
            found_cmd_103 = True

def make_szenario(spec, proc_template):
    template_proc = parse_process_template(proc_template)

    stream = ''
    for item in spec:
        tokens = item.split(',')
        
        activity_class = tokens[0]
        length = int(tokens[1])
        duedate = tokens[2]
        fix_tokens = tokens[3:]   
        
        proc = deepcopy(template_proc)  
        
        proc.set_duedate(duedate)
        proc.set_quantity(length)
        proc.set_activity_class(activity_class)
        proc.reassign_all()
        
        if len(fix_tokens) >= 3:
            #print(fix_tokens)
            idx_act = int(fix_tokens[0].split('=')[1])
            tp_start = fix_tokens[1].split('=')[1]
            tp_end = fix_tokens[2].split('=')[1]
            date_start, time_start = tp_start.split(' ')
            date_end, time_end = tp_end.split(' ') 
            proc.fix_activity(idx_act, date_start, time_start, date_end, time_end)
        
        stream += str(proc)

    return stream

def make_szenario_co_01(proc_template):
    szenario = [
        # mo to fr. 8 activities
        # <activity class>, <length (hours)>, <duedate>
        
        # 8x act of 1 hour length
        "A,1,27.02.2018",
        "B,1,27.02.2018",
        "C,1,27.02.2018",
        "A,1,27.02.2018",
        "B,1,27.02.2018",
        "C,1,27.02.2018",
        "A,1,27.02.2018",
        "B,1,27.02.2018",
        
        "C,1,28.02.2018",
        "A,1,28.02.2018",
        "B,1,28.02.2018",
        "C,1,28.02.2018",
        "A,1,28.02.2018",
        "B,1,28.02.2018",
        "C,1,28.02.2018",
        "A,1,28.02.2018",
        
        "B,1,01.03.2018",
        "C,1,01.03.2018",
        "A,1,01.03.2018",
        "B,1,01.03.2018",
        "C,1,01.03.2018",
        "A,1,01.03.2018",
        "B,1,01.03.2018",
        "C,1,01.03.2018",
        
        "A,1,02.03.2018",
        "B,1,02.03.2018",
        "C,1,02.03.2018",
        "A,1,02.03.2018",
        "B,1,02.03.2018",
        "C,1,02.03.2018",
        "A,1,02.03.2018",
        "B,1,02.03.2018",
        
        "C,1,03.03.2018",
        "A,1,03.03.2018",
        "B,1,03.03.2018",
        "C,1,03.03.2018",
        "A,1,03.03.2018",
        "B,1,03.03.2018",
        "C,1,03.03.2018",
        "A,1,03.03.2018",
        ]
    
    return make_szenario(szenario, proc_template)

def make_szenario_co_03(proc_template):
    szenario = [
        # mo 16 activities 
        # <activity class>, <length (hours)>, <duedate>
        
        # 8x act of 1 hour length
        "A,1,27.02.2018",
        "B,1,27.02.2018",
        "C,1,27.02.2018",
        "A,1,27.02.2018",
        "B,1,27.02.2018",
        "C,1,27.02.2018",
        "A,1,27.02.2018",
        "B,1,27.02.2018",
        
        # 8x act of 1 hour length
        "C,1,27.02.2018",
        "A,1,27.02.2018",
        "B,1,27.02.2018",
        "C,1,27.02.2018",
        "A,1,27.02.2018",
        "B,1,27.02.2018",
        "C,1,27.02.2018",
        "A,1,27.02.2018",
        ]
    
    return make_szenario(szenario, proc_template)

def make_szenario01(which_template):
    szenario = [
        # <activity class>, <length (hours)>, <duedate>
        "A,1,01.11.2017",
        "B,1,01.11.2017",
        "C,1,01.11.2017",
        
        "A,1,01.11.2017",
        "B,1,01.11.2017",
        "C,1,01.11.2017",
        
        "A,1,01.11.2017",
        "B,1,01.11.2017",
        "C,1,01.11.2017",
        
        "A,1,01.11.2017",
        "B,1,01.11.2017",
        "C,1,01.11.2017",
        
        "A,1,01.11.2017",
        "B,1,01.11.2017",
        "C,1,01.11.2017",
        
        "A,1,01.11.2017",
        "B,1,01.11.2017",
        "C,1,01.11.2017",
        
        "A,1,01.11.2017",
        "B,1,01.11.2017",
        "C,1,01.11.2017",
        
        "A,1,01.11.2017",
        "B,1,01.11.2017",
        "C,1,01.11.2017",
        ]
    
    return make_szenario(szenario, which_template)
    
def make_szenario02(which_template):
    szenario = [
        # <activity class>, <length (hours)>, <duedate>
        "A,2,23.02.2018",
        "B,2,23.02.2018",
        "C,2,23.02.2018",
        
        "A,2,23.02.2018",
        "B,2,23.02.2018",
        "C,2,23.02.2018",
        
        "A,2,23.02.2018",
        "B,2,23.02.2018",
        "C,2,23.02.2018",
        
        "A,2,23.02.2018",
        "B,2,23.02.2018",
        "C,2,23.02.2018",
        
        "A,2,23.02.2018",
        "B,2,23.02.2018",
        "C,2,23.02.2018",
        ################
        "A,2,24.02.2018",
        "B,2,24.02.2018",
        "C,2,24.02.2018",
        
        "A,2,24.02.2018",
        "B,2,24.02.2018",
        "C,2,24.02.2018",
        
        "A,2,24.02.2018",
        "B,2,24.02.2018",
        "C,2,24.02.2018",
        
        "A,2,24.02.2018",
        "B,2,24.02.2018",
        "C,2,24.02.2018",
        
        "A,2,24.02.2018",
        "B,2,24.02.2018",
        "C,2,24.02.2018",
        #################
        "A,2,25.02.2018",
        "B,2,25.02.2018",
        "C,2,25.02.2018",
        
        "A,2,25.02.2018",
        "B,2,25.02.2018",
        "C,2,25.02.2018",
        
        "A,2,25.02.2018",
        "B,2,25.02.2018",
        "C,2,25.02.2018",
        
        "A,2,25.02.2018",
        "B,2,25.02.2018",
        "C,2,25.02.2018",
        
        "A,2,25.02.2018",
        "B,2,25.02.2018",
        "C,2,25.02.2018",
        ]
    
    return make_szenario(szenario, which_template)    

def make_szenario_co_06(proc_template):
    szenario = [
        # mo to fr. 8 activities
        # <activity class>, <length (hours)>, <duedate>
        
        # 8x act of 1 hour length
        "A,1,27.02.2018",
        "B,1,27.02.2018",
        ",1,27.02.2018",
        "A,1,27.02.2018",
        "B,1,27.02.2018",
        ",1,27.02.2018",
        "A,1,27.02.2018",
        "B,1,27.02.2018",
        
        "A,1,28.02.2018",
        "B,1,28.02.2018",
        ",1,28.02.2018",
        "A,1,28.02.2018",
        "B,1,28.02.2018",
        ",1,28.02.2018",
        "A,1,28.02.2018",
        "B,1,28.02.2018",
        
        "A,1,01.03.2018",
        "B,1,01.03.2018",
        ",1,01.03.2018",
        "A,1,01.03.2018",
        "B,1,01.03.2018",
        ",1,01.03.2018",
        "A,1,01.03.2018",
        "B,1,01.03.2018",
        
        "A,1,02.03.2018",
        "B,1,02.03.2018",
        ",1,02.03.2018",
        "A,1,02.03.2018",
        "B,1,02.03.2018",
        ",1,02.03.2018",
        "A,1,02.03.2018",
        "B,1,02.03.2018",
        
        "A,1,03.03.2018",
        "B,1,03.03.2018",
        ",1,03.03.2018",
        "A,1,03.03.2018",
        "B,1,03.03.2018",
        "C,1,03.03.2018",
        "A,1,03.03.2018",
        "B,1,03.03.2018",
        ]
    
    return make_szenario(szenario, proc_template)

def make_szenario_co_07(proc_template):
    szenario = [
        # mo 3 x 8 processes
        # <activity class>, <length (hours)>, <duedate>
        
        # 8x act of 1 hour length
        "A,1,06.03.2018",
        "B,1,06.03.2018",
        "C,1,06.03.2018",
        "A,1,06.03.2018",
        "B,1,06.03.2018",
        "C,1,06.03.2018",
        "A,1,06.03.2018",
        "B,1,06.03.2018",
        
        "C,1,06.03.2018",
        "A,1,06.03.2018",
        "B,1,06.03.2018",
        "C,1,06.03.2018",
        "A,1,06.03.2018",
        "B,1,06.03.2018",
        "C,1,06.03.2018",
        "A,1,06.03.2018",
        
        "B,1,06.03.2018",
        "C,1,06.03.2018",
        "A,1,06.03.2018",
        "B,1,06.03.2018",
        "C,1,06.03.2018",
        "A,1,06.03.2018",
        "B,1,06.03.2018",
        "C,1,06.03.2018",
        ]
    
    return make_szenario(szenario, proc_template)

def make_szenario_co_08(proc_template):
    szenario = [
        # mo 3 x 8 processes
        # <activity class>, <length (hours)>, <duedate>
        
        # 8x act of 1 hour length
        "A,12,06.03.2018",
        "B,1,06.03.2018",
        "C,1,06.03.2018",
        "A,1,06.03.2018",
        "B,1,06.03.2018",
        "C,1,06.03.2018",
        "A,1,06.03.2018",
        "B,1,06.03.2018",
        
        "C,1,06.03.2018",
        "A,1,06.03.2018",
        "B,1,06.03.2018",
        "C,1,06.03.2018",
        "A,1,06.03.2018",
        "B,1,06.03.2018",
        "C,1,06.03.2018",
        "A,1,06.03.2018",
        
        "B,1,06.03.2018",
        "C,1,06.03.2018",
        "A,1,06.03.2018",
        "B,1,06.03.2018",
        "C,1,06.03.2018",
        "A,1,06.03.2018",
        "B,1,06.03.2018",
        "C,1,06.03.2018",
        ]
    
    return make_szenario(szenario, proc_template)

def make_szenario_co_09(proc_template):
    szenario = [
        # mo 3 x 8 processes
        # <activity class>, <length (hours)>, <duedate>
        
        # 8x act of 1 hour length
        "A,240,06.03.2018",
        "B,1,06.03.2018",
        "C,1,06.03.2018",
        "A,1,06.03.2018",
        "B,1,06.03.2018",
        "C,1,06.03.2018",
        "A,1,06.03.2018",
        "B,1,06.03.2018",
        
        "C,1,06.03.2018",
        "A,1,06.03.2018",
        "B,1,06.03.2018",
        "C,1,06.03.2018",
        "A,1,06.03.2018",
        "B,1,06.03.2018",
        "C,1,06.03.2018",
        "A,1,06.03.2018",
        
        "B,1,06.03.2018",
        "C,1,06.03.2018",
        "A,1,06.03.2018",
        "B,1,06.03.2018",
        "C,1,06.03.2018",
        "A,1,06.03.2018",
        "B,1,06.03.2018",
        "C,1,06.03.2018",
        ]
    
    return make_szenario(szenario, proc_template)
  

def make_szenario_co_10(proc_template):
    szenario = [
        # mo to fr. 8 activities
        # <activity class>, <length (hours)>, <duedate>
    
        # 8x act of 1 hour length
        "A,1,27.02.2018",
        "B,1,27.02.2018,fixact=0,start=05.03.2018 09:00,end=05.03.2018 10:00",
        "C,1,27.02.2018",
        "A,1,27.02.2018",
        "B,1,27.02.2018",
        "C,1,27.02.2018",
        "A,1,27.02.2018",
        "B,1,27.02.2018",
        
        "C,1,28.02.2018",
        "A,1,28.02.2018",
        "B,1,28.02.2018",
        "C,1,28.02.2018",
        "A,1,28.02.2018",
        "B,1,28.02.2018",
        "C,1,28.02.2018",
        "A,1,28.02.2018",
        
        "B,1,01.03.2018",
        "C,1,01.03.2018",
        "A,1,01.03.2018",
        "B,1,01.03.2018",
        "C,1,01.03.2018",
        "A,1,01.03.2018",
        "B,1,01.03.2018",
        "C,1,01.03.2018",
        
        "A,1,02.03.2018",
        "B,1,02.03.2018",
        "C,1,02.03.2018",
        "A,1,02.03.2018",
        "B,1,02.03.2018",
        "C,1,02.03.2018",
        "A,1,02.03.2018",
        "B,1,02.03.2018",
        
        "C,1,03.03.2018",
        "A,1,03.03.2018",
        "B,1,03.03.2018",
        "C,1,03.03.2018",
        "A,1,03.03.2018",
        "B,1,03.03.2018",
        "C,1,03.03.2018",
        "A,1,03.03.2018",
        ]
    
    return make_szenario(szenario, proc_template)  
    
def make_szenario_co_11(proc_template):
    szenario = [
        # mo to fr. 8 activities
        # <activity class>, <length (hours)>, <duedate>
    
        # 8x act of 1 hour length
        "A,1,27.02.2018",
        "B,1,27.02.2018,fixact=0,start=05.03.2018 09:00,end=05.03.2018 10:00",
        "C,1,27.02.2018,fixact=0,start=05.03.2018 09:00,end=05.03.2018 10:00",
        "A,1,27.02.2018",
        "B,1,27.02.2018",
        "C,1,27.02.2018",
        "A,1,27.02.2018",
        "B,1,27.02.2018",
        
        "C,1,28.02.2018",
        "A,1,28.02.2018",
        "B,1,28.02.2018",
        "C,1,28.02.2018",
        "A,1,28.02.2018",
        "B,1,28.02.2018",
        "C,1,28.02.2018",
        "A,1,28.02.2018",
        
        "B,1,01.03.2018",
        "C,1,01.03.2018",
        "A,1,01.03.2018",
        "B,1,01.03.2018",
        "C,1,01.03.2018",
        "A,1,01.03.2018",
        "B,1,01.03.2018",
        "C,1,01.03.2018",
        
        "A,1,02.03.2018",
        "B,1,02.03.2018",
        "C,1,02.03.2018",
        "A,1,02.03.2018",
        "B,1,02.03.2018",
        "C,1,02.03.2018",
        "A,1,02.03.2018",
        "B,1,02.03.2018",
        
        "C,1,03.03.2018",
        "A,1,03.03.2018",
        "B,1,03.03.2018",
        "C,1,03.03.2018",
        "A,1,03.03.2018",
        "B,1,03.03.2018",
        "C,1,03.03.2018",
        "A,1,03.03.2018",
        ]
    
    return make_szenario(szenario, proc_template)      
    
def make_szenario_co_12(proc_template):
    szenario = [
        # mo to fr. 8 activities
        # <activity class>, <length (hours)>, <duedate>
    
        # 8x act of 1 hour length
        "A,1,27.02.2018",
        "B,1,27.02.2018,fixact=0,start=05.03.2018 11:00,end=05.03.2018 12:00",
        "C,1,27.02.2018",
        "A,1,27.02.2018",
        "B,1,27.02.2018,fixact=0,start=05.03.2018 13:00,end=05.03.2018 14:00",
        "C,1,27.02.2018",
        "A,1,27.02.2018",
        "B,1,27.02.2018,fixact=0,start=05.03.2018 15:00,end=05.03.2018 16:00",
        
        "C,1,28.02.2018",
        "A,1,28.02.2018",
        "B,1,28.02.2018",
        "C,1,28.02.2018",
        "A,1,28.02.2018",
        "B,1,28.02.2018",
        "C,1,28.02.2018",
        "A,1,28.02.2018",
        
        "B,1,01.03.2018",
        "C,1,01.03.2018",
        "A,1,01.03.2018",
        "B,1,01.03.2018",
        "C,1,01.03.2018",
        "A,1,01.03.2018",
        "B,1,01.03.2018",
        "C,1,01.03.2018",
        
        "A,1,02.03.2018",
        "B,1,02.03.2018",
        "C,1,02.03.2018",
        "A,1,02.03.2018",
        "B,1,02.03.2018",
        "C,1,02.03.2018",
        "A,1,02.03.2018",
        "B,1,02.03.2018",
        
        "C,1,03.03.2018",
        "A,1,03.03.2018",
        "B,1,03.03.2018",
        "C,1,03.03.2018",
        "A,1,03.03.2018",
        "B,1,03.03.2018",
        "C,1,03.03.2018",
        "A,1,03.03.2018",
        ]
    
    return make_szenario(szenario, proc_template)          
    
def make_szenario_co_13(proc_template):
    szenario = [
        # mo to fr. 8 activities
        # <activity class>, <length (hours)>, <duedate>
    
        # 8x act of 1 hour length
        "B,1,27.02.2018,fixact=0,start=05.03.2018 11:00,end=05.03.2018 12:00",
        ]
    
    return make_szenario(szenario, proc_template)    
    
def make_szenarioRR(which_template):
    szenario = [
        # <activity class>, <length (hours)>, <duedate>
        "A,5,01.12.2017",
        "B,5,31.11.2017",
        "C,5,02.12.2017",
        
        "A,6,07.12.2017",
        "B,6,08.11.2017",
        "C,6,09.11.2017",
        ]
    
    return make_szenario(szenario, which_template)
    
def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('message_file', metavar='message_file', help='input message file')
    
    return parser.parse_args()        
        
def main():
    """main function"""
    args = parse_arguments()
    filename = args.message_file

    
    #szenario = make_szenario_co_01('setup01') # setup_cost_only_01.dat
    #szenario = make_szenario_co_01('setup02') # setup_cost_only_02.dat
    #szenario = make_szenario_co_03('setup03') # setup_cost_only_04.dat
    #szenario = make_szenario_co_03('setup04') # setup_cost_only_05.dat
    #szenario = make_szenario_co_06('setup01') # setup_cost_only_06.dat
    #szenario = make_szenario_co_07('setup05') # setup_cost_only_07.dat
    #szenario = make_szenario_co_08('setup06') # setup_cost_only_08.dat
    #szenario = make_szenario_co_09('setup06') # setup_cost_only_09.dat
    #szenario = make_szenario_co_10('setup01') # setup_cost_only_10.dat
    #szenario = make_szenario_co_11('setup01') # setup_cost_only_11.dat
    #szenario = make_szenario_co_12('setup01') # setup_cost_only_12.dat
    #szenario = make_szenario_co_12('setup03') # setup_cost_only_13.dat
    #szenario = make_szenario_co_12('setup04') # setup_cost_only_14.dat
    #szenario = make_szenario_co_01('setup07') # setup_cost_only_15.dat
    #szenario = make_szenario_co_01('setup08') # setup_cost_only_16.dat
    szenario = make_szenario_co_01('setup03') # setup_cost_only_17.dat
    
    #szenario = make_szenario02('2acts')
    #szenario += make_szenarioRR('r1_only')
    prepare_messagefile(filename, szenario)


if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
