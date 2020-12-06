# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: BaseItem.py
#
# description
"""\n\n
    Base class for activity, ...
"""

VERSION = '0.1'

#from command_mapper import CommandMapper
import re
import sys
import operator
from argparse import ArgumentParser

class BaseData(object):
    """Base item which holds tokens and command"""
    
    def __init__(self, tokens):
        self._tokens = tokens

class Process(BaseData):
    
    def __init__(self, tokens):
        BaseData.__init__(self, tokens)
    
    def __str__(self):
        #return "\t".join(self._tokens)
        return "%s %s %s %s is_head=%s is_temp=%s" % (self._tokens[0], self._tokens[1], self._tokens[2], self._tokens[3], 
                                                      self.is_head(), self.is_temp())
    
    def is_head(self):
        return self._tokens[16] == "1"
    
    def is_temp(self):
        return self._tokens[0][0] == "C"
        
    def material(self):
        mat = self._tokens[3]
        if self._tokens[4] != '':
            mat += "/var=%s" % self._tokens[4]
        if self._tokens[15] != '':
            mat += "/%s" % self._tokens[15]
        return mat
    
    @classmethod 
    def cmd(cls):
        return 370  # DEF_ERPCommandcreate_Process______

def get_key_regex(classes):
    keys = map(lambda x: str(x.cmd()), classes)
    return re.compile(r"^2\t(%s)" % "|".join(keys))

def parse_messagefile(messagefile, classes):
    items = []
    rgx_class = get_key_regex(classes)
    rgx_dataline = re.compile("^3\s+(.*)\n?")
    dataline = None
    idx = 0
    for line in open(messagefile):
        idx += 1
        hit = rgx_class.search(line)
        if hit:
            if dataline is not None:
                items.append(Process(dataline.split('\t')))
            dataline = None
        else:
            hit = rgx_dataline.search(line)
            if hit:
                dataline = hit.group(1)
    return items
            

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

    procs = parse_messagefile(args.message_file, [Process,])

    temp_procs = filter(lambda x: x.is_temp() and x.is_head(), procs)
    #print ("#temp=%d" % len(items))
    
    materials = {}
    cnt = 0
    for item in temp_procs:
        cnt += 1
        mat = item.material()
        if not mat in materials:
            materials.setdefault(mat, 0)
        materials[mat] += 1

    single_mats = filter(lambda x: materials[x] == 1, materials)
    cnt_single_mat = sum(1 for _ in single_mats)
     
    for mat, mat_cnt in sorted(materials.items(), key=operator.itemgetter(1)):
        print("%s    %d" % (mat, mat_cnt)) 
        
    print("\n#procs=%d" % len(procs) )
    print("#temp_mat=%d #mat=%d %0.1f" % (cnt, len(materials), cnt / len(materials)))
    print("#temp_mat which occur only once=%d %0.1f" % (cnt_single_mat, cnt_single_mat*100/len(materials)))
    
if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
    
    

