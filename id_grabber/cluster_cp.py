# -*- coding: ISO-8859-1 # Encoding declaration -*-
# file: cluster_cp.py
#
# description
"""\n\n
    take a *.dat file an shwo clusters of consumer producer


for each process
    pid = process.id()
    cp_info[pid].produced = produced_part(pid)
    cp_info[pid].consumed = consumed_parts(pid)

# eliminate non-relevant parts
relevant_parts = all_produced_parts
for each pid:
    cp_info[pid].consumed_parts = intersection(relevant_parts, cp_info[pid].consumed_parts)

# build clusters
handled_pids = empty_set
for each process
    pid = process.id()
    if pid in handled_ids: continue

    cluster_parts = empty_set
    cluster_parts.add( cp_info[pid].produced )
    cluster_parts.add( cp_info[pid].consumed )
    build_next_cluster
        iterate over all pids:
            add pids which intersect with cluster_parts
        ... until no pid found
"""

import sys
from tarjan import tarjan

mode61 = True

def tokenize(dataline):
    """split dataline into tokens"""
    return dataline[:-1].split('\t')

def is_head(dataline_process):
    """for a process dataline return true, if line describes a head process, false otherwise"""
    tokens = tokenize(dataline_process)
    return tokens[17] == '1'

def is_temp(dataline_process):
    """true if dataline describes a temporary process"""
    first_char = tokenize(dataline_process)[1][0].lower()
    return first_char == 'c'

def get_ppid(dataline_process):
    """get part process id (rueckmeldenummer)"""
    return tokenize(dataline_process)[3]

def get_prio(dataline_process):
    """get priority of process"""
    return tokenize(dataline_process)[11]

def get_freie_menge(dataline_process):
    """get 'freie menge' as a float"""
    val = tokenize(dataline_process)[18].replace(',', '.')
    return float(val)

def get_bg_ueber_lager(dataline_process):
    """true if process has flag 'baugruppe ueber lager'"""
    tokens = tokenize(dataline_process)
    if len(tokens) > 25:
        return tokens[25] == '1'
    return 0

def get_produced_part(dataline_process):
    """get produced part of process. Add '_FreieMange=0' if 'freie menge' is 0"""
    tokens = tokenize(dataline_process)
    part   = tokens[4]
    artvar = tokens[5]
    idx_charge = mode61 and 22 or 23
    charge = tokens[idx_charge]
    if get_freie_menge(dataline_process) == 0:
        return '%s|%s|%s_FreieMenge=0' % (part, artvar, charge)
    return '%s|%s|%s' % (part, artvar, charge)

def get_process_id(dataline_process):
    """get process id"""
    return tokenize(dataline_process)[2]

def material_get_process_id(dataline_material):
    """get part id out of dataline material"""
    return tokenize(dataline_material)[2]

def material_get_bedarfsmenge(dataline_material):
    """get requested amount out of dataline material"""
    val = tokenize(dataline_material)[8].replace(',', '.')
    return float(val)

def material_get_identact(dataline_material):
    """get identact out of dataline material"""
    return tokenize(dataline_material)[9]

def material_get_part(dataline_material):
    """get part id out of dataline material. Add '_FreieMange=0' if 'freie menge' is 0"""
    tokens   = tokenize(dataline_material)
    part     = tokens[6]
    artvar   = tokens[7]
    idx_charge = mode61 and 14 or 15
    charge   = tokens[idx_charge]
    result = '%s|%s|%s' % (part, artvar, charge)
    quantity = material_get_bedarfsmenge(dataline_material)
    #print("Material %s Bedarfsmenge %d" % (part, quantity))
    if quantity == 0:
        result += "_bedarfsmenge=0"
    return result

def process_cst_get_pid1(dataline_process_cst):
    """get process id of first process out of dataline process constraint"""
    return tokenize(dataline_process_cst)[2]

def process_cst_get_pid2(dataline_process_cst):
    """get process id of second process out of dataline process constraint"""
    return tokenize(dataline_process_cst)[4]

def activity_get_pid(dataline_activity):
    """get activity id out of dataline activity"""
    return tokenize(dataline_activity)[2]

def activity_get_ppid(dataline_activity):
    """get part process id out of dataline activity"""
    return tokenize(dataline_activity)[3]

def activity_get_actpos(dataline_activity):
    """get activity position out of dataline activity"""
    return int(tokenize(dataline_activity)[4])

def activity_get_identact(dataline_activity):
    """get identact out of dataline activity"""
    return tokenize(dataline_activity)[6]

def activity_is_fixed(dataline_activity):
    """true if activity is fixed (dataline activity)"""
    return tokenize(dataline_activity)[17] == '1'

def filter_irrelevant_parts(cp_infos):
    """filter all parts which are not consumed but not consumed"""
    relevant_parts = set()
    for pid in cp_infos:
        relevant_parts.add(cp_infos[pid]['produces'])
        relevant_parts.update(cp_infos[pid]['subproduces']) # ???
    for pid in cp_infos:
        cp_infos[pid]['consumes'] = relevant_parts.intersection(cp_infos[pid]['consumes'])

def does_intersect(cp_infos, cluster_produced_items, cluster_consumed_items, candidate_pid):
    """true if produced items intersect with consumed items of cluster"""
    consumed = cp_infos[candidate_pid]['consumes']
    intersect = cluster_produced_items.intersection(consumed)
    if intersect:
        return True
    produced = cp_infos[candidate_pid]['produces']
    return produced in cluster_consumed_items

def build_cluster(cp_infos, fixed_process_ids):
    """build cluster"""
    filter_irrelevant_parts(cp_infos)

    rounds = 0

    handled = set()
    cluster_pids = set()
    cluster_produced_items = set()
    cluster_consumed_items = set()
    for pid in cp_infos:
        if pid in handled:
            continue

        # start a new cluster
        if not cluster_pids:
            cluster_pids.add(pid)
            handled.add(pid)
            cluster_produced_items.add(cp_infos[pid]['produces'])
            cluster_consumed_items.update(cp_infos[pid]['consumes'])

        # a fixed process has its own cluster
        changed_flag = not pid in fixed_process_ids

        while changed_flag:
            rounds += 1
            changed_flag = False
            for proc_id in cp_infos:
                if proc_id in handled:
                    continue

                if proc_id in fixed_process_ids:
                    continue

                if does_intersect(cp_infos, cluster_produced_items, cluster_consumed_items, proc_id):
                    handled.add(proc_id)
                    changed_flag = True
                    cluster_pids.add(proc_id)
                    handled.add(proc_id)
                    cluster_produced_items.add(cp_infos[proc_id]['produces'])
                    cluster_consumed_items.update(cp_infos[proc_id]['consumes'])
                    break

        fixed = ''
        if cluster_pids.intersection(fixed_process_ids):
            fixed = '#'
        print('cluster %s#%d %s' % (fixed, len(cluster_pids), ', '.join(cluster_pids)))
        cluster_pids = set()
        cluster_produced_items = set()
        cluster_consumed_items = set()

    print('rounds: %d' % rounds)
    print('#procs: %d' % len(cp_infos))

def get_fixed_activities(filename):
    """get fixed activies"""
    fixed_activities = set()

    dataline = None
    for line in open(filename):
        # activity
        if line.find('2\t365') == 0:
            if dataline != None:
                if activity_is_fixed(dataline):
                    fixed_activities.add(activity_get_identact(dataline))
                dataline = None

        if line.find('3\t') == 0:
            dataline = line

    return fixed_activities

def get_fixed_processes(filename):
    """get set of process ids which are completely fixed"""
    fixed_info = {} # pid -> {'ppid' -> ppid, 'actpos' -> actpos, 'fixed' -> fixed }

    dataline = None
    for line in open(filename):
        # activity
        if line.find('2\t365') == 0:
            if dataline != None:
                pid   = activity_get_pid(dataline)
                ppid  = activity_get_ppid(dataline)
                pos   = activity_get_actpos(dataline)
                fixed = activity_is_fixed(dataline)

                fixed_info.setdefault(pid, {'ppid' : ppid, 'actpos' : pos, 'fixed' : fixed})
                info = fixed_info[pid]
                if ppid > info['ppid'] or \
                   ppid == info['ppid'] and pos > info['actpos']:
                    fixed_info[pid] = {'ppid' : ppid, 'actpos' : pos, 'fixed' : fixed}

        if line.find('3\t') == 0:
            dataline = line

    fixed_process_ids = set()
    for pid in fixed_info:
        #print pid, fixed_info[pid]
        if fixed_info[pid]['fixed']:
            fixed_process_ids.add(pid)

    return fixed_process_ids

def is_sub_producer(dataline):
    """baugruppe ueber lager and freie menge > 0"""
    bg_ueber_lager = get_bg_ueber_lager(dataline)
    quantity = get_freie_menge(dataline)
    return bg_ueber_lager and quantity > 0

def get_consumer_producer_info(filename, with_subproducer=False, with_fixed_activities=True):
    """go through datfile and call for each head process a special fct"""

    fixed_activities = set()
    if not with_fixed_activities:
        fixed_activities = get_fixed_activities(filename)
    #print('calculated fixed activities')

    process_infos = {}
    temp_proc_to_ppid = {}
    dataline = None
    for line in open(filename):
        # process
        if line.find('2\t370') == 0:
            if dataline != None:
                if is_head(dataline):
                    pid = get_process_id(dataline)
                    part = get_produced_part(dataline)
                elif is_temp(dataline) or not mode61:
                    pid = get_process_id(dataline)
                    part = get_produced_part(dataline)
                    ppid = get_ppid(dataline)
                    temp_proc_to_ppid.setdefault(pid, ppid)
                    if ppid > temp_proc_to_ppid[pid]:
                        continue
                    temp_proc_to_ppid[pid] = ppid
                elif with_subproducer and is_sub_producer(dataline):
                    pid = get_process_id(dataline)
                    part = get_produced_part(dataline)
                    process_infos.setdefault(pid, {'produces' : '', 'subproduces': set(), 'consumes' : set()})
                    process_infos[pid]['subproduces'].add(part)
                    continue
                else:
                    continue
                #print('process %s produces part %s' % (pid, part))
                process_infos.setdefault(pid, {'produces' : '', 'subproduces': set(), 'consumes' : set()})
                process_infos[pid]['produces'] = part

        # material
        if line.find('2\t355') == 0:
            if dataline != None:
                pid = material_get_process_id(dataline)
                part = material_get_part(dataline)
                identact = material_get_identact(dataline)

                """
                print("dataline '%s'" % dataline[:-1])
                print("pid '%s'" % pid)
                print("part '%s'" % part)
                print("identact '%s'" % identact)
                sys.exit(0)
                """

                if identact in fixed_activities:
                    pass
                    #print('Ignore because activity %s fixed, process %s consumes part %s' % (identact, pid, part))
                else:
                    #print('process %s consumes part %s' % (pid, part))
                    process_infos.setdefault(pid, {'produces' : '', 'subproduces': set(), 'consumes' : set()})
                    process_infos[pid]['consumes'].add(part)

        # process constraint (aob from process1 to process2)
        if line.find('2\t381') == 0:
            if dataline != None:
                pid1 = process_cst_get_pid1(dataline)
                pid2 = process_cst_get_pid2(dataline)
                part = "proc_cst_%s_%s" % (pid1, pid2)

                process_infos.setdefault(pid1, {'produces' : '', 'subproduces': set(), 'consumes' : set()})
                process_infos[pid1]['subproduces'].add(part)

                process_infos.setdefault(pid2, {'produces' : '', 'subproduces': set(), 'consumes' : set()})
                process_infos[pid2]['consumes'].add(part)

        if line.find('3\t') == 0:
            dataline = line

    return process_infos

def get_consumed(cp_infos, handled):
    """get consumed parts"""
    consumed = set()
    for pid in cp_infos:
        if not pid in handled:
            consumed.update(cp_infos[pid]['consumes'])
    return consumed

def get_produced(cp_infos, handled):
    """get produces inclusive subproduced parts of all consumber/producer infos"""
    produced = set()
    for pid in cp_infos:
        if not pid in handled:
            produced.add(cp_infos[pid]['produces'])
            produced.update(cp_infos[pid]['subproduces'])
    return produced

def get_produced_items(cp_infos, pid):
    """get produces items includive subproduced of one process"""
    produced = set()
    produced.add(cp_infos[pid]['produces'])
    produced.update(cp_infos[pid]['subproduces'])
    return produced

def calculate_dispolevel_old(cp_infos):
    """calculate dispolevel old style"""
    handled = set()
    level = -1
    changed_flag = True
    while True:
        changed_flag = False
        level += 1
        produced = get_produced(cp_infos, handled)
        for pid in cp_infos:
            if pid in handled:
                continue
            tmp_set = produced.intersection(cp_infos[pid]['consumes'])
            #print("tmp_set: %s" % produced)
            if not tmp_set:
                cp_infos[pid]['dispolevel'] = level
                handled.add(pid)
                changed_flag = True
        if not changed_flag:
            break

    for pid in cp_infos:
        if not pid in handled:
            cp_infos[pid]['dispolevel'] = level
        
    max_level = abs(level) - 1   
            
    for pid in cp_infos:
        cp_infos[pid]['dispolevel'] = abs(cp_infos[pid]['dispolevel'] - max_level)

def calculate_dispolevel(cp_infos):
    """calculate dispolvel new style"""
    handled = set()
    level = 0
    changed_flag = True
    while True:
        changed_flag = False
        consumed = get_consumed(cp_infos, handled)
        for pid in cp_infos:
            if pid in handled:
                continue
            
            intersection = consumed.intersection(get_produced_items(cp_infos, pid))
            """
            print("consumed %s intersection produced %s" % (get_produced_items(cp_infos, pid), consumed))
            if intersection:
                print("YEPP %s - intersection %s" % (pid, intersection))
            """
            #if not consumed.intersection(get_produced_items(cp_infos, pid)):
            if not intersection: 
            #if not cp_infos[pid]['produces'] in consumed: # do not consider subproduced stuff (contains proc_cst)
                #print("assign dpl %d to %s" % (level, pid))
                cp_infos[pid]['dispolevel'] = level
                handled.add(pid)
                changed_flag = True
        if not changed_flag:
            break
        level += 1

    for pid in cp_infos:
        if not pid in handled:
            cp_infos[pid]['dispolevel'] = level

def show_cp_infos(cp_infos, special_pids=None):
    """print consumer/producer info to console"""
    relevant_parts = set()
    pids = cp_infos.keys()
    if special_pids:
        pids = special_pids

    for pid in pids:
        relevant_parts.add(cp_infos[pid]['produces'])
        relevant_parts.update(cp_infos[pid]['subproduces'])
    for pid in pids:
        print('%s dispolevl %d produces %s' % (pid, cp_infos[pid]['dispolevel'], cp_infos[pid]['produces']))
        if 'subproduces' in cp_infos[pid]:
            print('subproduces: %s' % ', '.join(cp_infos[pid]['subproduces']))
        print('consumes:    %s' % ', '.join(relevant_parts.intersection(cp_infos[pid]['consumes'])))
        #print('consumes non relevant: %s' % ', '.join(cp_infos[pid]['consumes'].difference(relevant_parts)))
        print('')

def show_dispolevel(cp_infos):
    """print dispolevel to console"""
    levels = set()
    level_count = {}
    for pid in cp_infos:
        level = cp_infos[pid]['dispolevel']
        levels.add(level)
        level_count.setdefault(level, 0)
        level_count[level] += 1
    for level in reversed(list(levels)):
        print('------- level %d #%d' % (level, level_count[level]))
        for pid in cp_infos:
            if level != cp_infos[pid]['dispolevel']:
                continue
            print('%s dispolevel %d' % (pid, level))

def get_special_pids():
    """get special ids out of a file pids.txt"""
    filename = r"D:\devel\Testdaten61\work\dispolevel\pids.txt"
    pids = set()
    for line in open(filename):
        pid = line.strip()
        if pid:
            pids.add(pid)
    return pids

def calc_edge_infos(cp_infos):
    """return dictionary part -> set of proc ids
       where each part is mapped to the the process ids which consume this part
    """
    part_to_pids = {}
    for pid in cp_infos:
        for part in cp_infos[pid]['consumes']:
            part_to_pids.setdefault(part, set())
            part_to_pids[part].add(pid)
    return part_to_pids

def pids_to_indices(all_procs, pids, pid):
    """get list of all pid indices without 'self' pid"""
    indices = []
    for item in pids:
        if item != pid:
            indices.append(all_procs.index(item))
    return indices

def calc_cycle_detection_input(cp_infos):
    """return
        list of all processes, the index of a process within the list is important
        dictionary: process index -> [edges to other process indices]
    """
    tarjan_input = {}
    edge_info = calc_edge_infos(cp_infos)
    #for part in edge_info: print("part: %s\t%s" % (part, edge_info[part]))

    all_procs = list(cp_infos.keys())

    for idx, pid in enumerate(all_procs):
        consumer_pids = set()
        produced_items = get_produced_items(cp_infos, pid)
        for part in produced_items:
            if part in edge_info:
                consumer_pids.update(edge_info[part])
        indices = pids_to_indices(all_procs, consumer_pids, pid)
        #print("idx: %d, pid: %s, info: %s" % (idx, pid, indices))
        tarjan_input[idx] = indices
    #print("tarjan_input: %s" % tarjan_input)
    return all_procs, tarjan_input


def call_tarjan(input_string):
    """call cycle detection = tarjan algo
    sample1 = {1:[2],2:[1,5],3:[4],4:[3,5],5:[6],6:[7],7:[8],8:[6,9],9:[]}
    print(sample1)
    print(tarjan(sample1))
    print()
    """
    return tarjan(input_string)

def get_cycles(all_procs, tarjan_info):
    """map process indices to process ids, eleminate one element entries"""
    cycles = []
    for item in tarjan_info:
        if len(item) > 1:
            cycle = [all_procs[x] for x in item]
            cycles.append(cycle)
    return cycles

def main():
    """main function"""
    filename = sys.argv[1]

    with_subproducer = True
    # for cycle with baugruppe_ueber_lager set  get_consumer_producer_info(filename, True)
    cp_infos = get_consumer_producer_info(filename, with_subproducer)

    if 0:
        for proc_id in cp_infos:
            print(proc_id)
            print(cp_infos[proc_id])

    calculate_dispolevel(cp_infos)
    #show_dispolevel(cp_infos)
    #return
    #print('')

    show_cp_infos(cp_infos)
    #show_cp_infos(cp_infos, get_special_pids())

    #fixed_process_ids = get_fixed_processes(filename)
    """
    print
    for item in fixed_process_ids: print('FIXED proc id: %s' % item)
    print
    """

    #build_cluster(cp_infos, fixed_process_ids)

    filter_irrelevant_parts(cp_infos)
    all_procs, tarjan_input  = calc_cycle_detection_input(cp_infos)

    #print()
    #show_cp_infos(cp_infos)
    #print()

    #for idx, pid in enumerate(all_procs): print("%d\t%s" % (idx, pid))
    #print(tarjan_input)

    tarjan_output = call_tarjan(tarjan_input)
    # for cycle with baugruppe_ueber_lager set  get_consumer_producer_info(filename, True)
    cycles = get_cycles(all_procs, tarjan_output)
    print('cycles: %s' % cycles)

if __name__ == "__main__":
    try:
        main()
    except:
        print('Script failed')
        raise
