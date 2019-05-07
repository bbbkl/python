# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: message_file_reader.py
#
# description
"""\n\n
    read message file and perform some analyzation
"""

import re
import os
from argparse import ArgumentParser

from command_mapper import CommandMapper
from message.baseitem import BaseItem
from message.command_with_params import Command_OptimizeCTP
from message.serverinfo import ServerInfo, CheckErpID, P_ZeitMngEinh, LicInfo
from message.mb_activity import MbActivity, ActDispatch, ActSplit, BufferInfo
from message.mb_resoverl import MbResOverl, MaSelUebRess
from message.mb_resource import MbResource, MResourceKombination
from message.m_serverkennz import MServerKennz
from message.tr_activity import TrActivity
from message.md_artikel import MD_Artikel
from message.s_article import SArticle
from message.ml_artort import ML_ArtOrt
from message.ml_artortvar import ML_ArtOrtVar
from message.m_dispobew import M_DispoBew
from message.xcalendar import S_BetriebKal, M_Kalender, M_KalenderZeit, M_IntKalender, M_KalDatum, UpdateCalendar
from message.tr_resource import TrResource
from message.m_resource import M_Resource, M_ResAlt, M_ResAltGroup, UpdateResource
from message.tr_process import TrProcess, ProcessProd
from message.tr_material import TrMaterial
from message.tr_constraint import TrConstraint
from message.tr_processcst import TrProcessCst
from message.tr_timeconst import TrTimeConst
from message.mc_lager import McLager
from message.mc_charge import McCharge
from message.mc_art import McArt
from message.tr_stock import TrStock, TrStockFromMLArtOrtKomm
from message.m_ressgruppe import MRessGruppe
from message.m_uebort import M_UebOrt
from message.m_uebadresse import M_UebAdresse
from message.reason import ReasonMaterial, ReasonResource, ReasonResRes, ReasonTimebound, ReasonStructure, ReasonAdmin, ReasonHead, Reason, ReasonAct
from message.listener import APSCommandackSolutionCtpProd, JobContext, JobContextCtp, JobContextCtpProd, NoSolutionPPA, ContTimePoint
from message.schedulinginfo import SchedulingInfo, SchedulingTrigger
from message.sending_queue import DelSimulationMode, RollbackSimulationMode
from message.setup_matrix import SetupMatrix, SetupMatrixEntry, SetupPartFeature, SetupResourceFeature, SetupMatrixDefinition
from message.cmd_misc import CreateContTimePoint, CreateZeitMengenEinheit, SetDatabaseTime, MarkForGetSolCtpProd, GetSolutionCtpProd, GetSolutionCtp, SetConfigParam, UpdateActivity, UpdateResource
from message.cmd_delete_xy import DeleteProcessRueckNr, DeleteStaProcessRueckNr, DeleteStackProcess, DeleteProcess
#from message.m_ressaltgr import MRessAltGr
from time import time
from unhandled import Unhandled
from comm_mgr import CommMgr
from describe_command import describe_command, replace_codes

VERSION = "0.2"

ID_DATA1   = 1
ID_COMMAND = 2
ID_DATA    = 3
ID_COUNTER = 4

class MessageFileException(Exception):
    """ message file base exception """
    def __init__(self, what):
        Exception.__init__()
        self._what = what
    def what(self):
        """get exception description"""
        return self._what
        
class MessageLine:
    def __init__(self, tokens):        
        self._tokens = tokens
        
class Command(MessageLine):
    def __init__(self, tokens):
        MessageLine.__init__(self, tokens)
    def text(self):
        return CommandMapper.num2text()[int(self._tokens[0])]
    def cmd_id(self):
        return int(self._tokens[0])

class Data(MessageLine):
    def __init__(self, tokens):
        MessageLine.__init__(self, tokens)
        
class Counter(MessageLine):
    def __init__(self, tokens):
        MessageLine.__init__(self, tokens)

def do_skip(item, process_ids, regex_filter, skip_flag, inverse_flag):
    turn_on_cmds = ['CheckErpID', 'ServerInfo']
    if type(item).__name__ in turn_on_cmds:
        return False
    if type(item).__name__ != 'TrProcess':
        return skip_flag
    
    proc_id = item.process_id().strip()
    if regex_filter != '':
        hit = re.search(regex_filter, proc_id)
        if inverse_flag:
            return hit != None
        return hit == None
    if inverse_flag:
        return proc_id in process_ids
    else:
        return proc_id not in process_ids

END_OF_OTIMIZATION = CommandMapper.text2num()['DEF_ERPCommandEndOfJobComplete____']
START_OF_OPTIMIZATION = CommandMapper.text2num()['DEF_ERPCommandoptimize____________']
START_RECOGNIDED = False
def end_of_optimization(command):
    """true if command indicates 'end of optimization'"""
    global END_OF_OTIMIZATION, START_OF_OPTIMIZATION, START_RECOGNIDED
    START_RECOGNIDED = START_RECOGNIDED or command.cmd_id() == START_OF_OPTIMIZATION
    return START_RECOGNIDED and command.cmd_id() == END_OF_OTIMIZATION

def get_counter_value(filename, encoding_id):
    """0 if we have already a counter, the new counter value otherwise"""
    counter = 0
    for line in open(filename, encoding=encoding_id):
        if counter == 0 and line.find('\t') == -1:
            return -1 # we have already a counter line without a tab
        else:
            counter += 1
    return counter

def add_counter(filename, encoding_id):
    """add counter to given message file (for 5.2 compatibility)"""
    counter = get_counter_value(filename, encoding_id)
    if counter == -1: 
        return
    tmp_file = filename + "_tmp"
    output = open(tmp_file, 'w', encoding=encoding_id)
    output.write("%d\n" % counter)
    for line in open(filename, encoding=encoding_id):
        output.write(line)
    output.close()
    os.remove(filename)
    os.rename(tmp_file, filename)

def strip_message_file(filename, process_ids, regex_filter, describe_cmd, inverse_flag, encoding_id):
    """open file, read each line and rewrite it to message file only special processes"""
    
    result_file = get_output_file(filename, "stripped")
    output = open(result_file, "w", encoding=encoding_id)
    
    skip_flag = True
    data_line = None
    data = None
    for line in open(filename, encoding=encoding_id):
        line_type, tokens = parse_line(line)
        if line_type is None: continue
        if line_type == ID_COMMAND:
            command = Command(tokens)
            if data is not None:
                new_item = create_object(data, command)
                if new_item is not None:
                    skip_flag = do_skip(new_item, process_ids, regex_filter, skip_flag, inverse_flag)
                if not skip_flag:
                    output.write(data_line)
            else:
                skip_flag = False
                
            if not skip_flag:
                if describe_cmd:
                    line = describe_command(line)
                output.write(line)
                
            if end_of_optimization(command): 
                break 
            
            data = None
            data_line = None
        elif line_type == ID_DATA:
            data = tokens
            data_line = line
        elif line_type == ID_COUNTER or line_type == ID_DATA1:
            pass # strip counter stuff
        else:
            raise MessageFileException("unknown type (not in [1234] in message file line")
    output.close()
    add_counter(result_file, encoding_id)

def get_output_file(filename, description):
    """filename.ext -> filename_description.ext"""
    basepart, extension = os.path.splitext(filename)
    return "%s_%s%s" % (basepart, description, extension)

def flush_buffer(outstream, data_line, buffered_lines):
    """write data_line and buffered lines to outstream"""
    if data_line is not None:
        outstream.write(data_line)
    for line in buffered_lines:
        outstream.write(line)
    return None, []

def parse_line(line):
    """parse given line, return line type and tokens"""
    line_type = None
    tokens = []
    hit = re.search('^[1234]\t', line)
    if hit:
        line_type = int(line[0])
        tokens = get_tokens(line)
    return line_type, tokens

def get_tokens(line):
    """get data tokens out of given line"""
    if len(line):
        # some lines start with '1<tab>3<tab>...', handle them as '3<tab>...'
        if line[0] == '1':
            line = line[2:]
        if line[-1] != '\n':
            return line[2:].split('\t')
        else:
            return line[2:-1].split('\t')
    return []

def explain_message_file(filename, with_index_numbers, encoding_id):
    """open file, read each line and rewrite it to message file explained"""
    result_file = get_output_file(filename, "explained")
    output = open(result_file, "w", encoding=encoding_id)
    
    data_line = None
    data = None
    line_cnt = 0
    try:
        for line in open(filename, encoding=encoding_id):
            line_cnt += 1
            line_type, tokens =  parse_line(line)
            if line_type is None: continue
            if line_type == ID_COMMAND:
                command = Command(tokens)
                if data is not None:
                    new_item = create_object(data, command)
                    if new_item is not None:
                        try:
                            line_explained = new_item.line_with_description(with_index_numbers)
                            output.write(line_explained + '\n')
                        except:
                            output.write(data_line)
                            print(data_line)
                            print(line)
                            raise
                    data = None
                    data_line = None
                    continue
                cmd_text = command.text()
                if line.find(cmd_text)==-1: 
                    line = line[:-1] + " " + cmd_text + line[-1]
                output.write(line) # write command as well
            elif line_type == ID_DATA:
                data = tokens
                data_line = line
            elif line_type == ID_COUNTER or line_type == ID_DATA1:
                output.write(line)
                #items.append(Counter(tokens))
            else:
                raise MessageFileException("unknown type (not in [1234] in message file line")
    except:
        print("Failed in line=%d" % line_cnt)
        raise

def remove_fixations(filename, encoding_id):
    """open message file, remove all fixation of fixed activities, output goes to *_unfix file"""
    result_file = get_output_file(filename, "unfix")
    output = open(result_file, "w", encoding=encoding_id)
    
    data_line = None
    buffered_lines = [] # buffer for counter lines
    for line in open(filename, encoding=encoding_id):
        line_type, tokens = parse_line(line)
        if line_type == ID_COMMAND:
            command = Command(tokens)
            if command.cmd_id() == 365: # DEF_ERPCommandcreate_Activity_____
                if data_line:
                    tokens = TrActivity.unfix(get_tokens(data_line))
                    data_line = '3\t' + '\t'.join(tokens) + '\n'
            data_line, buffered_lines = flush_buffer(output, data_line, buffered_lines)
            output.write(line)
        elif line_type == ID_DATA:
            data_line, buffered_lines = flush_buffer(output, data_line, buffered_lines)
            data_line = line
        else:
            buffered_lines.append(line)
            
    flush_buffer(output, data_line, buffered_lines)
    output.close()

def grep_proc_ids(filename, res_id, encoding_id):
    """filter all proc ids which have a resource constraint with given res_id"""
    ids = set()
    data_line = None
    for line in open(filename, encoding=encoding_id):
        line_type, tokens = parse_line(line)
        if line_type == ID_COMMAND:
            command = Command(tokens)
            if command.cmd_id() == 350 and data_line: # DEF_ERPCommandcreate_Resource_____
                tokens = get_tokens(data_line)
                if tokens[6] == res_id:
                    ids.add(tokens[1]) # process id
        elif line_type == ID_DATA:
            data_line = line
    result = []
    result.extend(ids)
    return result

def read_message_file(filename, encoding_id):
    """open file, read each line and create appropriate object"""
    items = []
    data = None
    for line in open(filename, encoding=encoding_id):
        line_type, tokens = parse_line(line)
        if line_type is None: continue
        if line_type == ID_COMMAND:
            command = Command(tokens)
            if command.cmd_id() == 251: # DEF_ERPCommandEndOfJobComplete____ 
                break
            if data is not None:
                new_item = create_object(data, command)
                if new_item is not None:
                    items.append(new_item)
                data = None
            else:
                pass
                #items.append(command)
        elif line_type == ID_DATA:
            data = tokens
        elif line_type == ID_COUNTER or line_type == ID_DATA1:
            pass
            #items.append(Counter(tokens))
        else:
            raise MessageFileException("unknown type (not in [1234] in message file line")
    return items
    
id_to_class_mapping = None
def get_id_to_class_mapping():
    global id_to_class_mapping
    if id_to_class_mapping is None:
        id_to_class_mapping = {}
        classes = [MD_Artikel, SArticle, ServerInfo, P_ZeitMngEinh, LicInfo, TrActivity, 
                   MbActivity, ActDispatch, ActSplit, BufferInfo, MbResOverl, MaSelUebRess,
                   MbResource, MResourceKombination,
                   MServerKennz, M_DispoBew, 
                   S_BetriebKal, M_Kalender, M_KalenderZeit, M_IntKalender, 
                   M_KalDatum, UpdateCalendar,
                   TrResource, M_Resource, M_ResAlt, M_ResAltGroup, UpdateResource, 
                   TrProcess, ProcessProd,
                   TrMaterial, TrConstraint, TrProcessCst, McLager, McCharge, McArt, MRessGruppe,
                   TrTimeConst, 
                   ML_ArtOrt, ML_ArtOrtVar, M_UebOrt, M_UebAdresse, CheckErpID, TrStock, TrStockFromMLArtOrtKomm,
                   ReasonMaterial, ReasonResource, ReasonResRes, ReasonTimebound, ReasonStructure, ReasonAdmin,
                   ReasonHead, Reason, ReasonAct,
                   APSCommandackSolutionCtpProd, JobContext, JobContextCtp, JobContextCtpProd,
                   DelSimulationMode, RollbackSimulationMode,
                   SetupMatrix, SetupMatrixEntry, SetupPartFeature, SetupResourceFeature, SetupMatrixDefinition,
                   CreateContTimePoint, CreateZeitMengenEinheit, SetDatabaseTime, MarkForGetSolCtpProd, GetSolutionCtpProd, GetSolutionCtp, SetConfigParam, UpdateActivity, UpdateResource,
                   DeleteProcessRueckNr, DeleteStaProcessRueckNr, DeleteStackProcess, DeleteProcess,
                   Command_OptimizeCTP, NoSolutionPPA, ContTimePoint,
                   SchedulingInfo, SchedulingTrigger]
        for item in classes:
            for cmd_id in item.cmd_ids():
                id_to_class_mapping[cmd_id] = item 
    return id_to_class_mapping
    
handledCommands = []    
ignore = Unhandled.cmd_ids()
def create_object(data_tokens, command):
    """create object out of given message file line"""
    global ignore
    
    cmd = command.cmd_id()
    
    id_to_class = get_id_to_class_mapping()
    if cmd in id_to_class:
        return id_to_class[cmd](data_tokens, command)
    if cmd in ignore:
        return None
    
    global handledCommands
    if not command.text() in handledCommands:
        msg = "command not handled yet %s" % command.text()
        print(msg)
        handledCommands.append(command.text())
        #raise MessageFileException(msg)
    return None
        
def print_statistics(items):
    stats = {}
    for item in items:
        key = item.__class__.__module__
        stats.setdefault(key, 0)
        stats[key] += 1
    print("\n----- statistsic -----")
    for key in stats:
        print("%s: %d" % (key, stats[key]))
        
def check_resource_zero_belastungsgrenze(items):
    resources = [item for item in items if isinstance(item, M_Resource)]
    for resource in resources:
        if resource.belastungsgrenze() == 0.0:
            print("BELASTUNGRENZE 0, %s" % resource)
   
def check_activity_zero_intensity(items):
    activities = [item for item in items if isinstance(item, TrActivity)]
    for activity in activities:
        if activity.get_intensity() == 0.0:
            print("Intensitaet 0, %s" % activity)   
      
def get_filter_ids( arg_filter ):
    """check whether we have a filter file or explicit ids"""
    if os.path.isfile(arg_filter):
        arg_filter = open(arg_filter).readline()[:-1]
    return arg_filter.split(',')      
        
def print_activities(items):
    server_items = [item for item in items if isinstance(item, ServerInfo)]
    activities = [item for item in items if isinstance(item, TrActivity)]
    servertime = server_items[0].time()
    
    processing_time = 0
    early_time = 0
    fix_time = 0
    early_cnt = 0
    fix_cnt = 0
    for item in activities:
        activity_time = item.get_total_time_with_belastungsgrenze()
        processing_time += activity_time
        #print("activity: %s, time: %d" % (item.ident_part_proc_key(), activity_time))
        if item.start_time() < server_time:
            early_time += activity_time
            early_cnt += 1
        if item.fixiert(): 
            fix_cnt += 1
            fix_time += activity_time
     
    all_cnt = len(activities)
    print("\n#activites: %d" % all_cnt)
    print("#early: %d, (%05.2f %%)" % (early_cnt, early_cnt * 100.0 / all_cnt))  
    print("#fixed: %d, (%05.2f %%)" % (fix_cnt, fix_cnt * 100.0 / all_cnt))
    
    processing_time /= (60.0 * 24.0)
    print("#processing_time: %5.2f" % processing_time)
    early_time /= (60.0 * 24.0)
    pct = early_time * 100 / processing_time
    print("#early_time: %5.2f (%05.2f %%)" % (early_time, pct))  
    fix_time /= (60.0 * 24.0)
    pct = fix_time * 100 / processing_time
    print("#fix_time: %5.2f (%05.2f %%)" % (fix_time, pct))  
        
    return
    
    early = [item for item in activities if item.start_time() < servertime]
    after = [item for item in activities if item.start_time() >= servertime]
    print("\n\nEarly:")
    for item in early: print(item)
    print("\n --- server time: %s ---\n" % servertime)
    print("After:")
    for item in after: print(item)
    
def server_time(items):
    server_items = [item for item in items if isinstance(item, ServerInfo)]
    return server_items[0].time()    
  
def test_encoding(message_file):
    """check for file encoding"""
    encodings = ["UTF-8", "ISO-8859-1", "latin-1"]
    
    if not os.path.exists(message_file):
        raise FileNotFoundError(message_file)
    
    for item in encodings:
        try:
            for line in open(message_file, encoding=item):
                pass
            return item
        except:
            pass
        
    raise ("Cannot get right encoding, tried %s" % str(encodings))
          
        
def parse_arguments():
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    
    parser.add_argument('message_file', metavar='message_file', help='input message file')
    parser.add_argument('-m51', '--mode_51', action="store_true", # or stare_false
                      dest="mode_51", default=False, # negative store value
                      help="handle 5.1 message file")  
    parser.add_argument('-x', '--explain', action="store_true", # or stare_false
                      dest="explain", default=False, # negative store value
                      help="create explained message file")
    parser.add_argument('-d', '--describe_commands', action="store_true", # or stare_false
                      dest="describe_commands", default=False, # negative store value
                      help="add for each '2' command the corresponding definition text. The Message file remains usable.")  
    parser.add_argument('-f', '--filter', metavar='string', # or stare_false
                      dest="filter", default='', # negative store value
                      help="filter all processes out of message file except given ids (comma separated list)")
    parser.add_argument('-rf', '--regex-filter', metavar='string', # or stare_false
                      dest="regex_filter", default='', # negative store value
                      help="filter all processes out of message file which match given regular expression")
    parser.add_argument('-resf', '--res-filter', metavar='string', # or stare_false
                      dest="res_filter", default='', # negative store value
                      help="filter all processes out of message file which match given resource id")
    parser.add_argument('-i', '--inverse_filter', action="store_true", # or stare_false
                      dest="inverse_filter", default=False, # negative store value
                      help="inverse filter. filter only specified processes; all other remain.")  
    parser.add_argument('--unfix', action="store_true", # or stare_false
                      dest="remove_fixations", default=False, # negative store value
                      help="remove all fixations. generate <message_file>_unfix.dat") 
    parser.add_argument('-n', '--with_index_numbers', action="store_true", # or stare_false
                      dest="with_index_numbers", default=False, # negative store value
                      help="at index position to each explained field") 
    return parser.parse_args()
        
def main():
    """main function"""
    args = parse_arguments()
    
    encoding = test_encoding(args.message_file)
    
    if args.mode_51 == True:
        BaseItem.set_mode51()
    
    if args.remove_fixations == True:
        remove_fixations(args.message_file, encoding)
        return 0
    
    if args.explain == True:
        explain_message_file(args.message_file, args.with_index_numbers, encoding)
        return 0
    
    if args.regex_filter != '':
        strip_message_file(args.message_file, [], args.regex_filter, args.describe_commands, args.inverse_filter, encoding)
        return 0
    
    if args.res_filter != '':
        ids = grep_proc_ids(args.message_file, args.res_filter, encoding)
        print("filter ids='%s'" % ids)
        strip_message_file(args.message_file, ids, '', args.describe_commands, args.inverse_filter, encoding)
        return 0
    
    if args.filter != '':
        ids = get_filter_ids(args.filter)
        print("filter ids='%s'" % ids)
        strip_message_file(args.message_file, ids, '', args.describe_commands, args.inverse_filter, encoding)
        return 0
    
    if args.describe_commands:
        replace_codes(args.message_file, encoding)
        return 0

    try:
        t1 = time()
        items = read_message_file(args.message_file, encoding)
        t2 = time()
        print("num items: %d" % len(items))
        print("time diff: ", t2 - t1)
        
        print_statistics(items)
        
        print(server_time(items))
        check_resource_zero_belastungsgrenze(items)
        check_activity_zero_intensity(items)
        
        comm_mgr = CommMgr(items)
        
        comm_mgr.combine_resources()
        # test
        resources = [item for item in items if isinstance(item, TrResource)]
        with_m_resource = [item for item in resources if item.m_resource() is not None]
        print("#resource: %d, #with_m_resource: %d" % (len(resources), len(with_m_resource)))
        
        comm_mgr.add_zeitmengeneinheit_to_activities()
        comm_mgr.add_resources_to_activities()
        # test
        activities = [item for item in items if isinstance(item, TrActivity)]
        with_base_resource = [item for item in activities if item.get_base_resource() is not None]
        print("#actvities with base resource: %d" % len(with_base_resource))
        
        comm_mgr.add_processes_to_activities()
        #test
        with_process = [item for item in activities if item.get_process() is not None]
        print("#actvities with process: %d" % len(with_process))
        
        print_activities(items)
        
        comm_mgr.combine_artikel()
        artikel_all = [item for item in items if isinstance(item, SArticle)]
        for item in artikel_all:
            print(item, '\n')
        
    except MessageFileException as ex:
        print(ex.what())
        raise ex
    return 0

if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
