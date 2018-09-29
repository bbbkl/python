'''
Created on 20.06.2013

@author: Krueger_B
'''
import sys
import os

def separate_proc(filename, proc_id):
    cnt_last_match = 0
    cnt = 0
    package = 0
    base = os.path.join(os.path.dirname(filename), proc_id)
    take_next_flag = 0
    stream = open(base + "_%02d.txt" % package, "w")
    for line in open(filename):
        cnt += 1
        # skip lines with counter info
        if line.find("4\t")==0:
            continue
        if take_next_flag == 1:
            take_next_flag = 0
            stream.write(line)
        elif line.find(proc_id) != -1:
            if cnt - cnt_last_match > 5:
                stream.close()
                stream = open(base + "_%02d.txt" % package, "w")
                package += 1
            
            take_next_flag = 1
            stream.write(line)
            cnt_last_match = cnt

def main():
    """main function"""
    filename = sys.argv[1]
    proc_id = sys.argv[2]
    
    separate_proc(filename, proc_id)
    
    #grep_proc_begin_end(filename, resource_id)

if __name__ == '__main__':
    try:
        main()
    except:
        print('Script failed')
        raise