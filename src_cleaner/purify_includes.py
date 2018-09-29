# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: purify_includes.py
#
# description
"""\n\n
    ensure that includes contain first directory level (project) and own includes have quotes, system includes use brackets.
    Own include should come first
"""

import sys
import re
import os

def get_include_templates(start_dir):
    """for all <project>/<name>.h return <name>.h -> "project/name.h" """
    result = {}
    for (path, dirs, files) in os.walk(start_dir):
        src_files = [x for x in files if os.path.splitext(x)[-1] in [".h",]]
        for src_file in src_files:
            project = os.path.basename(path)
            result[src_file.lower()] = '%s/%s' % (project, src_file)
    result['svn_buildinfo.h'] = 'apsObjektmodell/svn_buildinfo.h'
    return result

def get_sourcefiles(start_dir):
    """get all *.cpp files"""
    result = []
    for (path, dirs, files) in os.walk(start_dir):
        src_files = [os.path.join(path, x) for x in files if os.path.splitext(x)[-1] in [".cpp",]]
        result.extend(src_files)
    
    result.sort() 
    return result

def get_headerfiles(start_dir):
    """get all *.cpp files"""
    result = []
    for (path, dirs, files) in os.walk(start_dir):
        src_files = [os.path.join(path, x) for x in files if os.path.splitext(x)[-1] in [".h",]]
        result.extend(src_files)
    
    result.sort() 
    return result

def get_project_name(srcfile):
    """get project name for given source file"""
    return os.path.basename(os.path.dirname(srcfile))

def strip_project(srcfile):
    prefix = os.path.basename(os.path.dirname(srcfile))
    if prefix.lower().find("aps") != -1:
        pos = srcfile.find(prefix) + len(prefix) + 1
        return srcfile[pos:]
    return srcfile

def get_src_includes(srcfile):
    """get existing includes of given srcfile"""
    includes = []

    for line in open(srcfile):
        if line.find('#include') != -1:
            hit = re.search(r'([^<"\s]+)[>"]', line)
            if not hit:
                print ("missed '%s'" % line)
            else:
                includes.append(strip_project(hit.group(1)))
    return includes

def get_header_filename(srcfile):
    return "%s.h" % os.path.splitext(os.path.basename(srcfile))[0]
    

def remove_include(src_include, include_names):
    include_names = [x.lower() for x in include_names]
    to_remove = []
    for item in src_include:
        if item.lower() in include_names:
            to_remove.append(item)
    for item in to_remove:
        src_include.remove(item)
    return src_include
        
def is_ilog(name):
    tokens = ['ilc', 'ilsolver', 'ils']
    for token in tokens:
        if name.lower().find(token)!=-1:
            return True
    return False
        
def get_otherlib_headers(src_includes, include_templates):
    result = []
    for name in src_includes:
        tmp = name.lower()
        if tmp.find('wx') != -1:
            result.append(name)
        if is_ilog(tmp):
            result.append(name)
        if tmp.find('gtest') != -1 or tmp.find('gmock') != -1:
            result.append(name)
        if tmp.find('psapi') != -1:
            result.append(name)
        
    return sorted(set(result))      
        
def get_system_headers(src_includes, include_templates):
    result = []  
    for name in src_includes:
        tmp = name.lower()
        if tmp in include_templates:
            continue
        if tmp.find('wx') != -1:
            continue
        if tmp.find('gtest') != -1 or tmp.find('gmock') != -1:
            continue
        if is_ilog(tmp):
            continue
        result.append(name)

    return sorted(result)
        
def get_expanded(src_includes, include_templates):
    result = []
    for name in src_includes:
        tmp = name.lower()
        if not tmp in include_templates:
            print ("Ooops", name)
            sys.exit(0)
        result.append(include_templates[tmp])
    
    return  sorted(set(result))       
        
def is_headerfile(srcfile):
    return os.path.splitext(srcfile)[1].find('h')        
        
def sort_includes(src_includes, include_templates, srcfile):
    result = []
    project_name = get_project_name(srcfile)
    newline_flag = False
    
    if not is_headerfile(srcfile):
        # 1. stdafx
        stdafx = 'stdafx.h'
        if stdafx in src_includes:
            result.append('"%s/%s"' % (project_name, stdafx))
            #result.append('"%s"' % stdafx)
            src_includes = remove_include(src_includes, [stdafx,])
            newline_flag = True
            
        # 2. own header
        own_name = get_header_filename(srcfile).lower()
        if own_name == stdafx:
            pass
        elif own_name in include_templates:
            result.append('"%s"' % include_templates[own_name])
            src_includes = remove_include(src_includes, [own_name,])
            newline_flag
        else:
            own_name = own_name.replace('test', '')
            if own_name in include_templates:
                result.append('"%s"' % include_templates[own_name])
                src_includes = remove_include(src_includes, [own_name,])
            newline_flag
    
    # 3. system headers
    system_headers = get_system_headers(src_includes, include_templates)
    if system_headers:
        if newline_flag: 
            result.append('')
        newline_flag = True
        for header in system_headers:
            result.append('<%s>' % header)
        src_includes = remove_include(src_includes, system_headers)
    
    # 4. other lib headers
    otherlib_headers = get_otherlib_headers(src_includes, include_templates)
    if otherlib_headers:
        if newline_flag: 
            result.append('')
        newline_flag = True
        for header in otherlib_headers:
            result.append('<%s>' % header)
        src_includes = remove_include(src_includes, otherlib_headers)
    
    # 5. expand own include
    expanded_headers = get_expanded(src_includes, include_templates)
    if expanded_headers:
        if newline_flag: 
            result.append('')
        newline_flag = True
        for header in expanded_headers:
            result.append('"%s"' % header)
        src_includes = remove_include(src_includes, otherlib_headers)
        
    return result
        
    
def get_pos_and_stripped_file(srcfile):
    pos = -1
    lines = []
    for line_idx, line in enumerate(open(srcfile)):
        if line.find('#include') != -1:
            if pos == -1:
                pos = line_idx
            continue
        lines.append(line)
    return (pos, lines)

def apply_includes(srcfile, includes, pos, lines):
    stream = open(srcfile, 'w')
    include_handled_flag = False
    for idx, line in enumerate(lines):
        if idx == pos:
            for include in includes:
                if include:
                    stream.write('#include %s\n' % include)
                else:
                    stream.write('\n')
            stream.write('\n')
            include_handled_flag = True
        if include_handled_flag and line.strip() == '':
            continue
        include_handled_flag = False
        
        stream.write(line)
    stream.close()    
    
def main():
    """main function"""
    start_dir = sys.argv[1]
    
    includes_templates = get_include_templates(start_dir)
    #srcfiles = get_sourcefiles(start_dir)
    srcfiles = get_headerfiles(start_dir)
    for srcfile in srcfiles:
        existing_includes = get_src_includes(srcfile)
        
        print ("\n%s" % srcfile)
        existing_includes = sort_includes(existing_includes, includes_templates, srcfile)
        for fn in existing_includes: print ('\t%s' % fn)
        
        pos, lines = get_pos_and_stripped_file(srcfile)
        if pos != -1:
            apply_includes(srcfile, existing_includes, pos, lines)
            pass

if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise