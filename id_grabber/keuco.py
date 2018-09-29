# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: keuco.py
#
# description
"""\n\n
    check integrity of optimizer data for listener (sonic data)
"""

import sys
import re

def enrich_datfile(dat_file):
    new_file = dat_file.replace(".dat", "_enriched.dat")
    stream = open(new_file, "w")
    line_count = 0
    dataline = None
    # 2    160    DEF_ERPCommanddeleteStackProcess__
    # 2    161    DEF_ERPCommanddeleteProcess_______
    # 2    370    DEF_ERPCommandcreate_Process______
    # 2    132    DEF_ERPCommandgetSolutionCtpProd__
    #
    rgxCmd = re.compile(r'^2\t(132|160|161|370)')
    for line in open(dat_file):
        line_count += 1
        if rgxCmd.search(line):
            if dataline is None:
                print("no data for command in line %d" % line_count)
            elif dataline[0] != '3':
                print("strange data for command in line %d" % line_count)
            if dataline.find("ST-10002127-00070") != -1:
                line = line[:-1] + " " + dataline
            dataline = None
        else:
            dataline = line
        stream.write(r"%s" % line)
        
    stream.close()
            
def main():
    """main function"""
    dat_file = sys.argv[1]
   
    enrich_datfile(dat_file)

if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
