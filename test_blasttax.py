import unittest
import re

from mock import *

import blasttax


names_dmp = '''1	|	all	|		|	synonym	|
1	|	root	|		|	scientific name	|
2	|	Bacteria	|	Bacteria <prokaryote>	|	scientific name	|
2	|	Monera	|	Monera <Bacteria>	|	in-part	|
2	|	Procaryotae	|	Procaryotae <Bacteria>	|	in-part	|
2	|	Prokaryota	|	Prokaryota <Bacteria>	|	in-part	|
2	|	Prokaryotae	|	Prokaryotae <Bacteria>	|	in-part	|
2	|	bacteria	|	bacteria <blast2>	|	blast name	|
2	|	eubacteria	|		|	genbank common name	|
2	|	not Bacteria Haeckel 1894	|		|	synonym	|
3	|	genusname	|	test	|		|
4	|	ordername	|	test	|		|
5	|	familyname	|	test	|		|
6	|	Azorhizobium	|		|	scientific name	|
6	|	Azorhizobium Dreyfus et al. 1988	|		|	synonym	|
6	|	Azotirhizobium	|		|	equivalent name	|
'''

nodes_dmp = '''1	|	1	|	no rank	|		|	8	|	0	|	1	|	0	|	0	|	0	|	0	|	0	|		|
2	|	3	|	species	|		|	0	|	0	|	11	|	0	|	0	|	0	|	0	|	0	|		|
3	|	4	|	genus	|		|	0	|	0	|	0	|	0	|	0	|	0	|	0	|	0	|		|
4	|	5	|	order	|		|	0	|	1	|	11	|	1	|	0	|	1	|	0	|	0	|		|
5	|	1	|	family	|	AC	|	0	|	1	|	11	|	1	|	0	|	1	|	1	|	0	|		|
6	|	1	|	species	|	AC	|	0	|	1	|	11	|	1	|	0	|	1	|	1	|	0	|		|
'''

div_dmp = '''0	|	BCT	|	Bacteria	|		|
1	|	INV	|	Invertebrates	|		|
2	|	MAM	|	Mammals	|		|
3	|	PHG	|	Phages	|		|
4	|	PLN	|	Plants	|		|
5	|	PRI	|	Primates	|		|
6	|	ROD	|	Rodents	|		|
7	|	SYN	|	Synthetic	|		|
8	|	UNA	|	Unassigned	|	No species nodes should inherit this division assignment	|
9	|	VRL	|	Viruses	|		|
10	|	VRT	|	Vertebrates	|		|
11	|	ENV	|	Environmental samples	|	Anonymous sequences cloned directly from the environment	|
'''

class TestNode(unittest.TestCase):
    def setUp(self):
        self.dmpline = nodes_dmp.splitlines()[0]

    def test_from_dmpline(self):
        print self.dmpline
        r = blasttax.Node(
            self.dmpline
        )
        self.assertEqual(r.id, '1')
        self.assertEqual(r.parent_id, '1')
        self.assertEqual(r.rank, 'no rank')
        self.assertEqual(r.division, '8')

    def test_from_parsed(self):
        l = re.split('\t\|\t', self.dmpline)
        r = blasttax.Node(l)
        self.assertEqual(r.id, '1')
        self.assertEqual(r.parent_id, '1')
        self.assertEqual(r.rank, 'no rank')
        self.assertEqual(r.division, '8')

    def test_empty_line(self):
        self.assertRaises(
            ValueError,
            blasttax.Node,
            ''
        )

    def test_line_has_to_many_items(self):
        self.assertRaises(
            ValueError, 
            blasttax.Node,
            '\t|\t'.join([str(i) for i in range(30)])
        )

class TestName(unittest.TestCase):
    def setUp(self):
        self.dmpline = names_dmp.splitlines()[2]

    def test_from_dmpline(self):
        r = blasttax.Name(
            self.dmpline
        )
        self.assertEqual(r.id, '2')
        self.assertEqual(r.name, 'Bacteria')

    def test_from_parsed(self):
        l = re.split('\t\|\t', self.dmpline)
        r = blasttax.Name(l)
        self.assertEqual(r.id, '2')
        self.assertEqual(r.name, 'Bacteria')

    def test_empty_line(self):
        self.assertRaises(
            ValueError,
            blasttax.Name,
            ''
        )

    def test_line_has_to_many_items(self):
        self.assertRaises(
            ValueError, 
            blasttax.Name,
            '\t|\t'.join([str(i) for i in range(30)])
        )

class TestDivision(unittest.TestCase):
    def setUp(self):
        self.dmpline = div_dmp.splitlines()[0]

    def test_from_dmpline(self):
        r = blasttax.Division(
            self.dmpline
        )
        self.assertEqual(r.id, '0')
        self.assertEqual(r.name, 'Bacteria')
        self.assertEqual(r.code, 'BCT')

    def test_from_parsed(self):
        l = re.split('\t\|\t', self.dmpline)
        r = blasttax.Division(l)
        self.assertEqual(r.id, '0')
        self.assertEqual(r.name, 'Bacteria')
        self.assertEqual(r.code, 'BCT')

    def test_empty_line(self):
        self.assertRaises(
            ValueError,
            blasttax.Division,
            ''
        )

    def test_line_has_to_many_items(self):
        self.assertRaises(
            ValueError, 
            blasttax.Division,
            '\t|\t'.join([str(i) for i in range(30)])
        )

class TestIndexDmpfile(unittest.TestCase):
    def test_indexes_by_id(self):
        with patch('__builtin__.open') as mopen:
            mopen.return_value.__enter__.return_value = names_dmp.splitlines()
            r = blasttax.index_dmpfile('/path/to/names.dmp', 'Name')
            self.assertEqual(r['1'][0].id, '1')
            self.assertEqual(r['1'][0].name, 'all')
            self.assertEqual(r['1'][1].id, '1')
            self.assertEqual(r['1'][1].name, 'root')

    def test_invalid_dmptype(self):
        self.assertRaises(
            ValueError,
            blasttax.index_dmpfile,
            '/path/to/nodes.dmp',
            'invalid'
        )

    def test_accepts_filehandle(self):
        handle = MagicMock(file)
        handle.__enter__.return_value = names_dmp.splitlines()
        r = blasttax.index_dmpfile(handle, 'Name')
        self.assertEqual(r['1'][0].id, '1')
        self.assertEqual(r['1'][0].name, 'all')
        self.assertEqual(r['1'][1].id, '1')
        self.assertEqual(r['1'][1].name, 'root')

class TestPhylo(unittest.TestCase):
    def setUp(self):
        self.divfh = MagicMock(file)
        self.nodefh = MagicMock(file)
        self.namefh = MagicMock(file)
        self.namefh.__enter__.return_value = names_dmp.splitlines()
        self.nodefh.__enter__.return_value = nodes_dmp.splitlines()
        self.divfh.__enter__.return_value = div_dmp.splitlines()
        self.nameindex = blasttax.index_dmpfile(self.namefh, 'Name')
        self.nodeindex = blasttax.index_dmpfile(self.nodefh, 'Node')
        self.divindex = blasttax.index_dmpfile(self.divfh, 'Division')

    def test_contains_correct_phylogony(self):
        r = blasttax.Phylo('2', self.nameindex, self.nodeindex, self.divindex)
        self.assertEqual(
            r.species,
            [
                'Bacteria', 'Monera', 'Procaryotae', 'Prokaryota',
                'Prokaryotae', 'bacteria', 'eubacteria', 'not Bacteria Haeckel 1894'
            ]
        )
        self.assertEqual(r.genus, ['genusname'])
        self.assertEqual(r.order, ['ordername'])
        self.assertEqual(r.family, ['familyname'])

    def test_no_phylo_for_taxid(self):
        self.assertRaises(
            ValueError,
            blasttax.Phylo,
            '99', self.nameindex, self.nodeindex, self.divindex
        )

    def test_str_returns_ordered_phylogony(self):
        e = 'Bacteria(species) -> genusname(genus) -> ordername(order) -> familyname(family)'
        r = blasttax.Phylo(
            '2', self.nameindex, self.nodeindex, self.divindex
        ).__str__()
        self.assertEquals(e, r)

    def test_str_returns_phylo_for_single_item(self):
        e = 'Azorhizobium(species)'
        r = blasttax.Phylo(
            '6', self.nameindex, self.nodeindex, self.divindex
        ).__str__()
        self.assertEquals(e, r)

class TestPhylogony(unittest.TestCase):
    def setUp(self):
        self.divfh = MagicMock(file)
        self.nodefh = MagicMock(file)
        self.namefh = MagicMock(file)
        self.namefh.__enter__.return_value = names_dmp.splitlines()
        self.nodefh.__enter__.return_value = nodes_dmp.splitlines()
        self.divfh.__enter__.return_value = div_dmp.splitlines()
        self.inst = blasttax.Phylogony(self.namefh, self.nodefh, self.divfh)

    def test_builds_correct_phlogony(self):
        r = self.inst['2']
        self.assertEqual(
            r.species,
            [
                'Bacteria', 'Monera', 'Procaryotae', 'Prokaryota',
                'Prokaryotae', 'bacteria', 'eubacteria', 'not Bacteria Haeckel 1894'
            ]
        )
        self.assertEqual(r.genus, ['genusname'])
        self.assertEqual(r.order, ['ordername'])
        self.assertEqual(r.family, ['familyname'])

    def test_no_taxid(self):
        self.assertRaises(KeyError, self.inst.__getitem__, '99')

    def test_only_builds_index_once(self):
        self.inst.nameindex = blasttax.index_dmpfile(self.namefh, 'Name')
        self.inst.nodeindex = blasttax.index_dmpfile(self.nodefh, 'Node')
        self.inst.divindex = blasttax.index_dmpfile(self.divfh, 'Division')
        with patch('blasttax.index_dmpfile') as mock:
            r = self.inst['1']
            r = self.inst['2']
            self.assertEqual(0, mock.call_count)
