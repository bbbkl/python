import sys
import os.path
import re

from collections import namedtuple

__all__ = ['tarjan',
           'tarjan_iter',
           'tarjan_recursive']

""" Context used to implement the algorithm without recursion in @tarjan
    and @tarjan_iter """
TarjanContext = namedtuple('TarjanContext',
                                ['g',           # the graph
                                 'S',           # The main stack of the alg.
                                 'S_set',       # == set(S) for performance
                                 'index',       # { v : <index of v> }
                                 'lowlink',     # { v : <lowlink of v> }
                                 'T',           # stack to replace recursion
                                 'ret'])        # return code

def _tarjan_head(ctx, v):
    """ Used by @tarjan and @tarjan_iter.  This is the head of the
        main iteration """
    ctx.index[v] = len(ctx.index)
    ctx.lowlink[v] = ctx.index[v]
    ctx.S.append(v)
    ctx.S_set.add(v)
    it = iter(ctx.g.get(v, ()))
    ctx.T.append((it,False,v,None))

def _tarjan_body(ctx, it, v):
    """ Used by @tarjan and @tarjan_iter.  This is the body of the
        main iteration """
    for w in it:
        if w not in ctx.index:
            ctx.T.append((it,True,v,w))
            _tarjan_head(ctx, w)
            return
        if w in ctx.S_set:
            ctx.lowlink[v] = min(ctx.lowlink[v], ctx.index[w])
    if ctx.lowlink[v] == ctx.index[v]:
        scc = []
        w = None
        while v != w:
            w = ctx.S.pop()
            scc.append(w)
            ctx.S_set.remove(w)
        ctx.ret.append(scc)

def tarjan_iter(g):
    """ Returns the strongly connected components of the graph @g
        in a topological order.

            @g is the graph represented as a dictionary
                    { <vertex> : <successors of vertex> }.

        This function does not recurse.  It returns an iterator. """
    ctx = TarjanContext(
        g = g,
        S = [],
        S_set = set(),
        index = {},
        lowlink = {},
        T = [],
        ret = [])
    main_iter = iter(g)
    while True:
        try:
            v = next(main_iter)
        except StopIteration:
            return
        if v not in ctx.index:
            _tarjan_head(ctx, v)
        while ctx.T:
            it, inside, v, w = ctx.T.pop()
            if inside:
                ctx.lowlink[v] = min(ctx.lowlink[w], ctx.lowlink[v])
            _tarjan_body(ctx, it, v)
            if ctx.ret:
                assert len(ctx.ret) == 1
                yield ctx.ret.pop()

def tarjan(g):
    """ Returns the strongly connected components of the graph @g
        in a topological order.

            @g is the graph represented as a dictionary
                    { <vertex> : <successors of vertex> }.
    
        This function does not recurse. """
    ctx = TarjanContext(
            g = g,
            S = [],
            S_set = set(),
            index = {},
            lowlink = {},
            T = [],
            ret = [])
    main_iter = iter(g)
    while True:
        try:
            v = next(main_iter)
        except StopIteration:
            return ctx.ret
        if v not in ctx.index:
            _tarjan_head(ctx, v)
        while ctx.T:
            it, inside, v, w = ctx.T.pop()
            if inside:
                ctx.lowlink[v] = min(ctx.lowlink[w], ctx.lowlink[v])
            _tarjan_body(ctx, it, v)

def tarjan_recursive(g):
    """ Returns the strongly connected components of the graph @g
        in a topological order.

            @g is the graph represented as a dictionary
                    { <vertex> : <successors of vertex> }.
                    
        This function recurses --- large graphs may cause a stack
        overflow. """
    S = []
    S_set = set()
    index = {}
    lowlink = {}
    ret = []

    def visit(v):
        index[v] = len(index)
        lowlink[v] = index[v]
        S.append(v)
        S_set.add(v)
        for w in g.get(v,()):
            if w not in index:
                visit(w)
                lowlink[v] = min(lowlink[w], lowlink[v])
            elif w in S_set:
                lowlink[v] = min(lowlink[v], index[w])
        if lowlink[v] == index[v]:
            scc = []
            w = None
            while v != w:
                w = S.pop()
                scc.append(w)
                S_set.remove(w)
            ret.append(scc)

    for v in g:
        if not v in index:
            visit(v)
    return ret

def strip_result(raw_data):
    for i in range(len(raw_data), 0, -1):
        if len(raw_data[i-1]) < 2:
            del raw_data[i-1]
    return raw_data


def parse_successor_infos(input_file):
    """
    input is a json file TT_M_DispoOrderSuccessor.json created at end of syncJointProducts in mavmrp00.p 
    temp-table bTT_M_DispoOrderSuccessor:write-json('file':U, 'D:/tmp/TT_M_DispoOrderSuccessor.json', yes).
    """
    rgx_part = re.compile(r'Artikel".*"([^"]*)"')
    rgx_var = re.compile(r'ArtVar".*"([^"]*)"')
    rgx_mrparea = re.compile(r'MRPArea"[^0-9]+(\d+)')
    rgx_part_s = re.compile(r'ArtikelSuccessor".*"([^"]*)"')
    rgx_var_s = re.compile(r'ArtikelVarSuccessor.*"([^"]*)"')
    rgx_mrparea_s = re.compile(r'MRPAreaSuccessor[^0-9]+(\d+)')
    
    successors = {}
    
    part = var = mrp = part_s = var_s = mrp_s = None
    for line in open(input_file):
        hit = rgx_part.search(line)
        if hit:
            part = hit.group(1)
            continue
        hit = rgx_var.search(line)
        if hit:
            var = hit.group(1)
            continue
        hit = rgx_mrparea.search(line)
        if hit:
            mrp = hit.group(1)
            continue
        hit = rgx_part_s.search(line)
        if hit:
            part_s = hit.group(1)
            continue
        hit = rgx_var_s.search(line)
        if hit:
            var_s = hit.group(1)
            continue
        hit = rgx_mrparea_s.search(line)
        if hit:
            mrp_s = hit.group(1)
            v = "/" + var if var else ""
            vs = "/" + var_s if var_s else ""
            
            a = "%s%s/%s" % (part,v,mrp)
            b = "%s%s/%s" % (part_s,vs,mrp_s)
            successors.setdefault(a, [])
            successors[a].append(b)
    
    for key in successors:
        print("%s -> %s" % (key, successors[key]))
    print()
    for key in successors:
        if key in successors[key]:
            print("direct circle %s <-> %s" % (key, key))
    print(strip_result(tarjan(successors)))


def main():

    sample1 = {1:[2],2:[1,5],3:[4],4:[3,5],5:[6],6:[7],7:[8],8:[6,9],9:[]}
    print(sample1)
    print(tarjan(sample1))
    print(strip_result(tarjan(sample1)))
    print()

    sample2 = {1:[2],2:[1,5],3:[4],4:[3,5],5:[6],6:[7],7:[8],8:[6,9],9:[6]}
    print(sample2)
    print(tarjan(sample2))
    print()

    sample3 = {1:[2],2:[1,5],3:[4],4:[3,5],5:[6],6:[7],7:[8],8:[6,9],9:[1]}
    print(sample3)
    print(tarjan(sample3))
    print()

    sample4 = {1:[2],2:[1,3,5],3:[4],4:[3,5],5:[6],6:[7],7:[8],8:[6,9],9:[1]}
    print(sample4)
    print(tarjan(sample4))

if __name__ == '__main__':
    try:
        main()
    except:
        print('Script failed')
        raise