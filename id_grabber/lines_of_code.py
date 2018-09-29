# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: lines_of_code.py
#
# description
"""\n\n
    for given start dir, sum up all lines of code of contained *.cpp *.h files
"""

import re
import os.path
from argparse import ArgumentParser

VERSION = '0.1'
  
class WhereClause:
    def __init__(self, srcfile, line_no, lines):
        self._srcfile = srcfile
        self._line_no = line_no
        self._lines = lines
  
    def __str__(self):
        #return self._srcfile
        res = "%s:%d\n" % (self._srcfile, self._line_no)
        for line in self._lines:
            res += line
        return res
  
    def stripped_line(self, line):
        rgx_comment = re.compile('(/\*.*\*/)')
        rgx_in_frame = re.compile('(not.*(?:=.*|in frame|matches|begins))')
        tmp = line.lower()
        tmp = tmp.replace('not can', '')
        tmp = tmp.replace('not (', '')
        tmp = tmp.replace('not contain', '')
        tmp = tmp.replace('not lookup', '')
        tmp = tmp.replace('if not', '')
        hit = rgx_comment.search(tmp)
        if not hit:
            hit = rgx_in_frame.search(tmp)
        if hit:
            tmp = tmp.replace(hit.group(1), '')
        return tmp
    
    def contains_not(self):
        for line in self._lines:
            tmp = self.stripped_line(line)
            if tmp.find('not ')!=-1:
                #print('machted line "%s"' % tmp)
                return True
        return False
    
    def is_candidate2(self):
        rgx = re.compile(r'(can\-find|find first|find last)')
        for line in self._lines:
            tmp = self.stripped_line(line)
            if rgx.search(tmp):
                return False
        return True
    
    def is_candidate(self):
        #rgx = re.compile(r'not b?tt')
        rgx = re.compile(r'\sbegins\s')
        for line in self._lines:
            tmp = self.stripped_line(line)
            if rgx.search(tmp):
                return self.is_candidate2()
                #return True
        return False
  
def is_comment_or_empty(line):
    return re.match(r'^\s*((\\|/\*).*)$', line) != None   
  
def count_lines(filename):
    try:
        count = 0
        for line in open(filename):
            if not is_comment_or_empty(line):
                count = count + 1
        return count
    except:
        print("failed on %s" % filename)
    return 0
  
def check_index_usage(filename):
    rgx_start = re.compile(r'[^"\']\bfind\b') #re.compile(r'[^"\']\bwhere\b')
    rgx_comment = re.compile('/\*.*\*/')
    rgx_end = re.compile(r'[.:]\s*$')
    try:
        lines = []
        line_no = 0
        for line in open(filename):
            in_item = (len(lines) > 0)
            line_no += 1
            if rgx_start.search(line.lower()) and not rgx_comment.search(line):
                lines.append(line)
                in_item = True
            elif in_item:
                lines.append(line)
            if in_item and rgx_end.search(line):
                item = WhereClause(filename, line_no, lines)
                lines = []
                if(item.is_candidate()):
                    print(item) 
            
    except:
        print("failed on %s" % filename)
    return 0  
  
def crawl_dir(start_dir):
    loc = 0
    file_count = 0
    #extensions = ('.h', '.cpp') # hier durch die eigenen Extensionen ersetzen
    extensions = ('.p', '.w', '.cls', '.if', '.tdf', '.lib')
    for root, dirs, files in os.walk(start_dir):
        relevant_files = list(filter(lambda x: os.path.splitext(x)[1] in extensions, files))
        file_count = file_count + len(relevant_files)
        for fn in relevant_files:
            #loc = loc + count_lines(os.path.join(root, fn))
            check_index_usage(os.path.join(root, fn))
    
    print("#files: %d, lines_of_code: %d" % (file_count, loc))
        
def parse_arguments():
    """parse arguments from command line"""
    #usage = "usage: %(prog)s [options] <message file>" + DESCRIPTION
    parser = ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('startdir', metavar='start_dir', help='input start dir')

    return parser.parse_args()        
        
def main():
    """main function"""
    args = parse_arguments()
    start_dir = args.startdir
    
    
    crawl_dir(start_dir)
    

if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
