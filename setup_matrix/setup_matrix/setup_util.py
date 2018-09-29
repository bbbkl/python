# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: setup_matrix.py
#
# description
"""\n\n
    setup matrix stuff
"""

import os.path
from argparse import ArgumentParser

VERSION = '0.1'

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

def get_entry_id(nth):
    """get id of nth matrix entry"""
    return chr(ord('A') + nth)        
    
def dist(a, b):
    """distance a to b"""
    return abs(ord(a) - ord(b))  
        
def cost(a, b):
    """penalty points / cost to setup from a to b"""
    return dist(a, b)
            
def pct(a, b, matrix_size):
    """percentage = tr time in percent for setup a->b"""
    unit = 100.0 / (matrix_size - 1)
    return dist(a, b) * unit
        
def get_matrix_property(ac_val):
    """get matrix property for given activity class value"""
    property_type = 5 # ESetupMatrixPropertyType ActivityClass   
    classification_system = ''
    feature = ''
    specification = ''
    part = ''
    part_variant = ''
    activity_class = ac_val
    resource_type = -1
    resource = ''
    
    items = [property_type, classification_system, feature, specification, part, part_variant, 
             activity_class, resource_type, resource]
    
    return to_line(items)[:-1]
         
def get_setup_matrix_id():
    return 'setup matrix id'        
         
def get_matrix_entry(x, y, matrix_size):
    """get matrix entry for activity class values x -> y"""
    matrix_id = get_setup_matrix_id()
    percent = pct(x, y, matrix_size)
    points = cost(x, y)
    property_x = get_matrix_property(x)
    property_y = get_matrix_property(y)
    
    items = [matrix_id, percent, points, property_x, property_y]
    
    return to_line(items)[:-1]

def get_matrix_entry_cmd(x, y, matrx_size):
    """get data line together with one entry line"""
    data_line = '3\t' + get_matrix_entry(x, y, matrx_size)
    cmd_line = '2\t396' # 396 = DEF_ERPCommandcreate_SetupMatrixEn
    return '%s\n%s\n' % (data_line, cmd_line)
    
def get_create_setup_matrix_cmd(matrix_id):
    """get create setup matrix command"""
    data_line = '3\t%s' % matrix_id
    cmd_line = '2\t395' # 395 = DEF_ERPCommandcreate_SetupMatrix__
    return '%s\n%s\n' % (data_line, cmd_line)
        
        
def setup_matrix(matrix_size, stream):
    """create message file lines for matrix with matrix_size dimension"""
    print('setup matrix size=%d' % matrix_size)
    for y in range(matrix_size):
        id_y = get_entry_id(y)
        for x in range(matrix_size):
            id_x = get_entry_id(x)
            #print("%s -> %s %d %d" % (id_y, id_x, cost(id_y, id_x), pct(id_y, id_x, matrix_size)))
            stream.write(get_matrix_entry_cmd(id_x, id_y, matrix_size))
            
def write_setup_matrix(matrix_size, stream):
    """write setup matrix info to stream"""
    matrix_id = get_setup_matrix_id()
    stream.write(get_create_setup_matrix_cmd(matrix_id)) 
    setup_matrix(matrix_size, stream)
            
def parse_resources(messagefile, encoding_id):
    """parse all resources contained in message file, print them enumerated to console"""
    data_line = None
    resources = set()
    for line in open(messagefile, encoding=encoding_id):
        if line.find('2\t311')==0: # 311    DEF_ERPCommandcreate_M_Ressource__
            if data_line is not None:
                tokens = tokenize(data_line)
                if len(tokens) > 2:
                    resources.add((tokens[1], tokens[2]))
            data_line = None
        else:
            data_line = line

    for idx, res in enumerate(sorted(resources)):
        print('%03d %s' % (idx, str(res)))

def get_resources(raw_resources):
    tokens = raw_resources.split(',')
    return [x.split(':') for x in tokens]

def set_activity_class(activity_line, value):
    """set given value as activity class in given activity line"""
    tokens = tokenize(activity_line)
    tokens[32] = value
    return to_line(tokens)

def tokenize(line):
    tokens = line.split('\t')
    tokens[-1] = tokens[-1][:-1]
    return tokens

def to_line(tokens):
    """return joined tokens"""
    return '\t'.join([str(x) for x in tokens]) + '\n'

def get_process_id(activity_line):
    return tokenize(activity_line)[2]

def get_next_value(process_id, current_value, num_values):
    """if process_id is same as before value remains, otherwise return another one"""
    if get_next_value.prev_proc_id == process_id:
        return current_value
    get_next_value.prev_proc_id = process_id
    if current_value is None:
        return 'A'
    idx = ord('A') + (ord(current_value)-ord('A')+1) % num_values
    val = chr(idx)
    # print("next val='%s' old='%s'" % (val, current_value))
    return val 
get_next_value.prev_proc_id = None
    

def get_resource_info(resource_line):
    """return tuple category / resource_id"""
    tokens = tokenize(resource_line)
    return [tokens[1], tokens[2]]

def set_setup_matrix_id(resource_line, matrix_id):
    """add setup matrix id to m_resource line"""
    tokens = tokenize(resource_line)
    while len(tokens) < 20:
        tokens.append('')
    tokens[19] = matrix_id
    return to_line(tokens)

def is_activity_line(line):
    return line is not None and line.count('\t') > 35

def modify_messagefile(messagefile, setup_resources, num_values, encoding_id):
    """assgign to each activity an activity class value"""
    prev_line = None
    fn_out = messagefile.replace('.dat', '.with_setupinfo.dat')
    out = open(fn_out, 'w', encoding=encoding_id)
    act_class_value = None
    for line in open(messagefile, encoding=encoding_id):
        if line.find('2\t365')==0: # 365    DEF_ERPCommandcreate_Activity_____
            if is_activity_line(prev_line):
                proc_id = get_process_id(prev_line)
                act_class_value = get_next_value(proc_id, act_class_value, num_values)
                prev_line = set_activity_class(prev_line, act_class_value)
        if line.find('2\t311')==0: # 311    DEF_ERPCommandcreate_M_Ressource__
            if prev_line:
                res_info = get_resource_info(prev_line)
                if res_info in setup_resources:
                    prev_line = set_setup_matrix_id(prev_line, get_setup_matrix_id())
        if prev_line:
            out.write(prev_line)
            if prev_line.find('2\t185')==0: # 185    DEF_ERPCommandsend_Depot__________
                write_setup_matrix(num_values, out)
            
        prev_line = line
    if prev_line:
        out.write(prev_line)
    out.close()

def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('message_file', metavar='message_file', help='input message file')
    parser.add_argument('resources', metavar='resources', nargs='?',
                        help='comma separated list of resource <category>:<res_id>')
    parser.add_argument('-m', '--matrix-size', metavar='matrix_size', type=int, default=5, 
                        help='size of setup matrix')
    parser.add_argument('-p', '--parse_resources', action="store_true", dest='parse_resources', 
                        default=False, help="grep ids of resources")
    return parser.parse_args()        
        
def main():
    """main function"""
    args = parse_arguments()
    filename = args.message_file
    
    encoding_id = test_encoding(filename)
    
    if args.parse_resources:
        parse_resources(filename, encoding_id)
        return 0
    
    resources = get_resources(args.resources)
    print(resources)
    
    modify_messagefile(filename, resources, args.matrix_size, encoding_id)
    
    #setup_matrix(args.matrix_size)


if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
