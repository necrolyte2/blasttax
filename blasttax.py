from __future__ import absolute_import, division, print_function

try:
    from builtins import open
except ImportError as e:
    from __builtin__ import open

import os
import os.path
import glob
import re
import collections
import argparse

__version__ = '0.0.1-dev'

class DmpLine(object):
    def __init__(self, dmpline):
        if isinstance(dmpline, str):
            self.parse(dmpline, self.headers)
        elif hasattr(dmpline, '__iter__'):
            self._setattrs(dmpline, self.headers)
        else:
            raise ValueError('Invalid dmpline encountered {0}'.format(dmpline))

    def _setattrs(self, parseddmpline, headers):
        if len(parseddmpline) != len(headers):
            raise ValueError('Expected {0} values but got {1}'.format(
                len(headers),
                len(parseddmpline)
            ))
        for hdr, value in zip(headers,parseddmpline):
            setattr(self, hdr, value)

    def parse(self, dmpline, headers):
        splitline = re.split('\t\|\t', dmpline)
        self._setattrs(splitline, headers)

class Node(DmpLine):
    headers = (
        'id', # node id in GenBank taxonomy database                  
        'parent_id', # parent node id in GenBank taxonomy database       
        'rank', # rank of this node (superkingdom, kingdom, ...)        
        'embl_code', # locus-name prefix; not unique                         
        'division', # see division.dmp file                                 
        'inherited_div_flag',  # (1 or 0) 1 if node inherits division from parent   
        'genetic_code_id', # see gencode.dmp file                              
        'inherited_ GC_flag', # (1 or 0) 1 if node inherits genetic code from parent
        'mitochondrial_genetic_code_id', # see gencode.dmp file                      
        'inherited_MGC_flag', # (1 or 0) 1 if node inherits mitochondrial gencode from parent
        'GenBank_hidden_flag', # (1 or 0) 1 if name is suppressed in GenBank entry lineage
        'hidden_subtree_root_flag', # (1 or 0) 1 if this subtree has no sequence data yet
        'comments', # free-text comments and citations     
    )

class Name(DmpLine):
    headers = (
		'id', # the id of node associated with this name              
		'name', # name itself                                           
        'unique_name', # the unique variant of this name if name not unique    
        'name_class', # (synonym, common name, ...)            
    )

class Division(DmpLine):
    headers = (
 		'id', # taxonomy database division id                         
        'code', # GenBank division code (three characters)          
        'name', # e.g. BCT, PLN, VRT, MAM, PRI...                   
        'comments'
    )

classmap = {
    'Node': Node,
    'Name': Name,
    'Division': Division,
}

def index_dmpfile(input_f, dmptype):
    '''
    Simply return a dictionary keyed by the id of each of the parsed lines.
    Each value is a list of parsed objects since some ids may be present
    multiple times

    :param str input_f: File handle or filepath to input .dmp file
    :param str dmptype: one of classmap's keys
    '''
    dmptype = classmap.get(dmptype, None)
    if dmptype is None:
        raise ValueError('{0} is not a valid dmptype'.format(dmptype))
    handle = input_f
    if isinstance(handle, str):
        handle = open(handle)
    index = collections.defaultdict(list)
    with handle as fh:
        for dmpline in fh:
            entry = dmptype(dmpline)
            index[entry.id].append(entry)
    return index

class Phylo(object):
    def __init__(self, taxid, nameindex, nodeindex, divindex):
        self.nameindex = nameindex
        self.nodeindex = nodeindex
        self.divindex = divindex
        self.taxid = taxid
        if self.taxid not in nameindex:
            raise ValueError('taxid {0} is missing from nameindex'.format(
                self.taxid
            ))
        if self.taxid not in nodeindex:
            raise ValueError('taxid {0} is missing from nodeindex'.format(
                self.taxid
            ))
    
    def __getattr__(self, attr):
        if attr not in self.__dict__:
            try:
                self._build_phylogony(self.taxid)
            except IndexError as e:
                pass
        try:
            return self.__dict__[attr]
        except KeyError as e:
            raise AttributeError('Phylo object has no attribute \'{0}\''.format(
                attr
            ))

    def _build_phylogony(self, taxid):
        '''
        From a given taxid build the full phylogony
        The taxid will be recursively looked up in the nodes/names
        '''
        if 'phylo' not in self.__dict__:
            self.__dict__['phylo'] = []
        else:
            return
        curnames, curnode, curdiv = self._get_name_node_div(taxid)
        self.phylo.append((curnames, curnode, curdiv))
        while curnames[0].name != 'all':
            names = self._get_attrs_for_(curnames, 'name')
            setattr(self, curnode.rank, names)
            curnames, curnode, curdiv = self._get_name_node_div(curnode.parent_id)
            if curnames[0].name != 'all':
                self.phylo.append((curnames, curnode, curdiv))

    def _get_attrs_for_(self, objs, attr):
        '''
        Returns all the attr from a list of objects as a list
        '''
        values = []
        for obj in objs:
            value = getattr(obj, attr)
            values.append(value)
        return values

    def _get_name_node_div(self, taxid):
        '''
        Looks up name, node and div in each of the indexes for the taxid
        and returns them all
        '''
        name = self.nameindex[taxid]
        node = self.nodeindex[taxid][0]
        divid = node.division
        div = self.divindex[divid]
        return name, node, div

    def __str__(self):
        phylo = []
        for names, node, div in self.phylo:
            _str = '{0}({1})'.format(names[0].name, node.rank)
            phylo.append(_str)
        return ' -> '.join(phylo)

class Phylogony(object):
    def __init__(self, namefh, nodefh, divfh):
        self.namefh = namefh
        self.nodefh = nodefh
        self.divfh = divfh

    def _build_indexes(self):
        if not hasattr(self, 'nameindex'):
            self.nameindex = index_dmpfile(self.namefh, 'Name')
        if not hasattr(self, 'nodeindex'):
            self.nodeindex = index_dmpfile(self.nodefh, 'Node')
        if not hasattr(self, 'divindex'):
            self.divindex = index_dmpfile(self.divfh, 'Division')

    def __getitem__(self, key):
        self._build_indexes()
        try:
            return Phylo(key, self.nameindex, self.nodeindex, self.divindex)
        except ValueError as e:
            raise KeyError(str(e))

def main():
    args = parse_args()
    p = Phylogony(args.namedmp, args.nodedmp, args.divisiondmp)
    print(p[args.taxid])

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'namedmp',
        help='names.dmp file'
    )

    parser.add_argument(
        'nodedmp',
        help='nodes.dmp file'
    )

    parser.add_argument(
        'divisiondmp',
        help='division.dmp'
    )

    parser.add_argument(
        'taxid',
        help='taxid to lookup phylogony for'
    )

    return parser.parse_args()

if __name__ == '__main__':
    main()
