# -*- coding: UTF-8 # Encoding declaration -*-
# file: aps_log_check.py
#
# description
"""\n\n
    grep import info out of given aps log file(s)
"""
import re
# import re
from argparse import ArgumentParser
import os.path
# import shutil
from glob import glob
from enum import Enum

VERSION = '0.1'

def get_input(source):
    result = []
    if os.path.isfile(source):
        result.append(source)
    else:
        result = glob(os.path.join(source, "*.log"))
    return result

class Log(Enum):
    DIFF_STOCKS = 1
    CFG_CONFLICT = 2
    CFG_KEY_UNKNOWN = 3
    D_ERR = 4
    IGNORE = 5
    MBJOB00004 = 6
    STOP_CONDITION = 7
    APP_ERR = 8
    MEM_ERR = 9
    INWB_CONNECT = 10
    MIN_WBZ = 11
    CFG_ACM_UNKNOWN = 12
    INTERNAL_ERROR_DISPLAYING = 13
    SONIC_RETRY = 14
    ACT_VERY_LONG = 15
    RESET_WITH_SUBPRODUCERS = 16
    TDR_FAIL = 17
    YES_NO = 18
    NO_LOCKFILE = 19
    ERR_DAT = 20
    STREAM_CURRUPT = 21
    STREAM_BLOCK_COUNTER = 22
    APSDATETIME = 23
    DMC_ERROR_FRW = 24
    STRUCTURED_EXCEPTION = 25
    TDR_NEG_MAT = 26
    LOCATION_OF_CATCH = 27
    FWD_OPTIMAL_DEMAND_TIMES = 28
    POOL_NUM_SPLITS = 29
    POOL_NO_SELECTED_INTENSITY = 30
    STATE_NO_OBJ_MODEL = 31
    STREAM_CMD_MISSING = 32
    PROCESS_LOCK_ERR = 33
    RESERVATION_DANGLING = 34
    NOT_ENOUGH_INTENSITY = 35
    STATE_ERR = 36
    UNKNOWN_EXCEPTION = 37
    RESTART_NECESSARY = 38
    ERR_REPORTED_ONCE = 39
    RESET_BOTTLENECK = 40
    PREC_CST_DOUBLET = 41
    MD_MRPSuggestion = 42
    TDR_NO_ACT_ADDED = 43
    PARTPROC_WITH_NO_ACT = 44
    SHOW_ERR_MDISP000015 = 45
    CAL_PROBLEM = 46
    EVENT_SUBSCRIBE_PROBLEM = 47
    NO_SOLUTION_PROCESS = 48
    DEPOT_IS_MISSING = 49
    INTERFACE_CLEARED = 50
    FILE_OPEN_ERR = 51
    DEPOT_PRODUCTING_ACT_NOT_FOUND = 52
    INVALID_DATE = 53
    CYCLE = 54
    MBJOB00003 = 55
    STREAM_CMD_UNEXPECTED = 56
    SONIC_JMS_ERR = 57
    SONIC_ON_EXCEPION = 58
    EXCEPION_ACCESS_VIOLATION = 59
    NO_FROZEN_PREDECESSOR = 60
    PROCESS_REORDERING = 61
    EXCEPTION_LOCATION = 62
    DISABLE_ENDS_BEFORE = 63
    LOAD_SERVER = 64
    RUNNING_SERVER_DETECTED = 65
    UNCLEAN_PREVIOUS_SHUTDOWN = 66
    TDR_PROBLEM = 67
    DEPOT_PROBLEM = 68
    INVALID_MSG_LINE = 69
    BOUNDING = 70
    MEM_BAD_ALLOC = 71
    SOL_CURSOR = 72

    UNKNOWN = 999

class Header(Enum):
    HOST = 1
    OPTI_VERSION = 2
    MAX_USEFUL_THREADS = 3
    REVISION_NUMBER = 4

    UNKNOWN = 998

def get_header_key_values():
    return { \
        "running on host" : Header.HOST,
        "max\_useful\_threads" : Header.MAX_USEFUL_THREADS,
        "proALPHA APS-Server version" : Header.OPTI_VERSION,
        "Revision Number\:" : Header.REVISION_NUMBER,
    }

def get_general_info(line):
    for key, val in get_header_key_values().items():
        if re.search(key, line, re.IGNORECASE):
          return val
    return Log.UNKNOWN

def get_rgx_header():
    expression = '|'.join(get_header_key_values().keys())
    return re.compile(r"(%s)" % expression, re.IGNORECASE)

def get_category(line):
    categories = {r"ML_Artort with different stocks" : Log.DIFF_STOCKS,
                  r"Config-entry (.*) is defined as" : Log.CFG_CONFLICT,
                  r"Raising STOP condition" : Log.STOP_CONDITION,
                  r"d_-err-\d{5}": Log.D_ERR,
                  r"d_-app-\d{5}" : Log.APP_ERR,
                  "(solthrowonerror|SolThrowOnError)" : Log.IGNORE,
                  "unknown config key" : Log.CFG_KEY_UNKNOWN,
                  "Unknown parameter '.*' used in optsrv.ini" : Log.CFG_KEY_UNKNOWN,
                  r"Unknown parameter '.*' sent by ERP": Log.CFG_ACM_UNKNOWN,
                  "mbjob00004" : Log.MBJOB00004,
                  "connecting integration workbench after 60 tries" : Log.INWB_CONNECT,
                  "Memory violation" : Log.MEM_ERR,
                  "The minimal WBZ for" : Log.MIN_WBZ,
                  "retry=" : Log.SONIC_RETRY,
                  "Very long activity" : Log.ACT_VERY_LONG,
                  "reset withSubproducers to false" : Log.RESET_WITH_SUBPRODUCERS,
                  "Internal error while displaying" : Log.INTERNAL_ERROR_DISPLAYING,
                  "Fail in tardiness reasoning" : Log.TDR_FAIL,
                  "Unhandled exception from executeTardinessReasoning" : Log.TDR_FAIL,
                  "Skipping timebound reason" : Log.TDR_PROBLEM,
                  "Complete verified material resource reason" : Log.TDR_PROBLEM,
                  "reason not calculated due to time limits" : Log.TDR_PROBLEM,
                  "Skipping material reason" : Log.TDR_PROBLEM,
                  "Reason determination failed for act set" : Log.TDR_FAIL,
                  "Negative material reason detected" : Log.TDR_NEG_MAT,
                  "Skipping resource reason, no activities were added" : Log.TDR_NO_ACT_ADDED,
                  "tried to read no/yes" : Log.YES_NO,
                  "Could not find lockfile" : Log.NO_LOCKFILE,
                  "corrupted data stream" : Log.STREAM_CURRUPT,
                  "Message sequence begin without expected command" : Log.STREAM_CMD_MISSING,
                  "Inconsistent message block counter" : Log.STREAM_BLOCK_COUNTER,
                  "Message counter was restarted" : Log.STREAM_BLOCK_COUNTER,
                  "in function: ApsDateTime" : Log.APSDATETIME,
                  "on an invalid ApsDateTime" : Log.APSDATETIME,
                  "Structured Exception caught" : Log.STRUCTURED_EXCEPTION,
                  "location of catch: Error in file" : Log.LOCATION_OF_CATCH,
                  "ERROR: Exception occured, type" : Log.UNKNOWN_EXCEPTION,
                  "Fatal error occured and restart is necessary" : Log.RESTART_NECESSARY,
                  "Forward scheduling in optimal demand times" : Log.FWD_OPTIMAL_DEMAND_TIMES,
                  "pool-res warning: numSplits" : Log.POOL_NUM_SPLITS,
                  "no selected intensity for activity scheduled with split on discrete resource pool" : Log.POOL_NO_SELECTED_INTENSITY,
                  "No ObjectModel available" : Log.STATE_NO_OBJ_MODEL,
                  "Server has ERROR-State" : Log.STATE_ERR,
                  "SERVER_STATE: Fatal error" : Log.STATE_ERR,
                  "ERP DEF_APSCommandSetServerState______ Error" : Log.STATE_ERR,
                  "processLockError" : Log.PROCESS_LOCK_ERR,
                  "dangling_reservations" : Log.RESERVATION_DANGLING,
                  "Can\'t be planned within horizon:" : Log.NOT_ENOUGH_INTENSITY,
                  "error is only reported once" : Log.ERR_REPORTED_ONCE,
                  "Reset bottleneck flag to false" : Log.RESET_BOTTLENECK,
                  "Precedence cst doublet count" : Log.PREC_CST_DOUBLET,
                  "dsMD_MRPSuggestion" : Log.MD_MRPSuggestion,
                  "skipping part process with no activities" : Log.PARTPROC_WITH_NO_ACT,
                  "mdisp000015 .* showError" : Log.SHOW_ERR_MDISP000015,
                  "Calendar of resource.*is not defined until end" : Log.CAL_PROBLEM,
                  "Using empty resource calendar" : Log.CAL_PROBLEM,
                  "has already subscribed to the evtMessageDisplayed" : Log.EVENT_SUBSCRIBE_PROBLEM,
                  "No Solution found for process" : Log.NO_SOLUTION_PROCESS,
                  "demand discarded because depot is missing" : Log.DEPOT_IS_MISSING,
                  "producing act not found" : Log.DEPOT_PRODUCTING_ACT_NOT_FOUND,
                  "Interface is cleared with uncopied elements" : Log.INTERFACE_CLEARED,
                  "File Open error" : Log.FILE_OPEN_ERR,
                  "Invalid date=" : Log.INVALID_DATE,
                  "unknown exception caught" : Log.UNKNOWN_EXCEPTION,
                  "Exception occured, type: ApsError" : Log.UNKNOWN_EXCEPTION,
                  "cycle \(by precedence constraints\)" : Log.CYCLE,
                  "it contains or is member of a cycle" : Log.CYCLE,
                  "mbjob00003 in terminateOptJobs" : Log.MBJOB00003,
                  "unexpected command received" : Log.STREAM_CMD_UNEXPECTED,
                  "while sending data to sonicMQ" : Log.SONIC_JMS_ERR,
                  "ApsSonicConnection::onException" : Log.SONIC_ON_EXCEPION,
                  "EXCEPTION_ACCESS_VIOLATION" : Log.EXCEPION_ACCESS_VIOLATION,
                  "CreateIlogModelProcessCst not frozen predecessor" : Log.NO_FROZEN_PREDECESSOR,
                  "Error during producer reordering" : Log.PROCESS_REORDERING,
                  "location of exception" : Log.EXCEPTION_LOCATION,
                  "Error in file.*at line": Log.EXCEPTION_LOCATION,
                  "constructing ApsError with info" : Log.EXCEPTION_LOCATION,
                  "disable EndsBefore" : Log.DISABLE_ENDS_BEFORE,
                  "Failed to load server" : Log.LOAD_SERVER,
                  "running APS-Server detected" : Log.RUNNING_SERVER_DETECTED,
                  "Unclean shutdown of previous run" : Log.UNCLEAN_PREVIOUS_SHUTDOWN,
                  "Depot \(S\), used in activity" : Log.DEPOT_PROBLEM,
                  "requested depot is not available" : Log.DEPOT_PROBLEM,
                  "Invalid activity message line" : Log.INVALID_MSG_LINE,
                  "Bounding in assignment based schedule failed" : Log.BOUNDING,
                  "Bounding in continuous production failed" : Log.BOUNDING,
                  "bad_alloc" : Log.MEM_BAD_ALLOC,
                  "create cursor out of function" : Log.SOL_CURSOR,

                  "_error.dat": Log.ERR_DAT,
                  "DMCErrorFrw": Log.DMC_ERROR_FRW,
                }
    for key in categories:
        if re.search(key, line):
            return categories[key]
    return Log.UNKNOWN

def parse_logfile(logfile):
    cat2line = {}
    header2line = {}
    rgx_header = get_rgx_header()
    idx = 0
    with open(logfile, "r") as stream:
        for line in stream:
            idx += 1
            if re.search(r"(error|warning|retry=)", line, re.IGNORECASE):
                category = get_category(line)
                cat2line.setdefault(category, [])
                cat2line[category].append(line)
                if category == Log.UNKNOWN: print("%s, %s\n" % (line[:-1], logfile))
            if rgx_header.search(line):
                key = get_general_info(line)
                header2line.setdefault(key, [])
                header2line[key].append(line)

    return cat2line, header2line

def check_logs(logfiles):
    cat2line = {}
    header2line = {}
    for fn in logfiles:
        category_infos, header_infos = parse_logfile(fn)
        for cat, lines in category_infos.items():
            cat2line.setdefault(cat, [])
            cat2line[cat].extend(lines)
        for key, lines in header_infos.items():
            header2line.setdefault(key, [])
            header2line[key].extend(lines)

    """
    if Log.UNKNOWN in cat2line:
        for line in cat2line[Log.UNKNOWN]:
            print(line[:-1])
    """
    print()
    for cat, lines in cat2line.items():
        print("#%s=%d" % (cat, len(lines)))
    print()
    for key, lines in header2line.items():
        print("#%s=%d" % (key, len(lines)))

def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('source', metavar='source', help='input logfile or directory with logfiles')

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

    logfiles = get_input(args.source)
    check_logs(logfiles)
    
if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
