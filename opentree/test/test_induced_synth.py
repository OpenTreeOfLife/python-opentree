import unittest
from dendropy import Tree
from opentree import OT


class TestInducedSynth(unittest.TestCase):
    def test_demands_id_arg(self):
        with self.assertRaises(ValueError):
            OT.synth_induced_tree()

    def test_int_ott_ids(self):
        with self.assertRaises(ValueError):
            OT.synth_induced_tree(ott_ids=["hi"])

    def test_success_ott_ids(self):
        OT.synth_induced_tree(ott_ids=[417950, 770315])
    
    def test_success_node_ids(self):
        OT.synth_induced_tree(node_ids=['ott417950', 'ott770315'])
    
    def test_success_mixed_ids(self):
        OT.synth_induced_tree(node_ids=['ott770315'], ott_ids=[417950])

class TestSynthNodes(object):
    """docstring for TestSynthNodeInfo"""
    def test_synth_node_info(self):
        resp = OT.synth_node_info(node_id='mrcaott354607ott374748')
        assert resp.response_dict['supported_by'] == {'ot_1344@Tr105486': 'Tn16531763'}

    def test_synth_subtree_node(self):
        OT.synth_subtree(node_id='mrcaott354607ott374748')

    def test_synth_subtree_bad_ott(self):
        assert 'broken' in OT.synth_subtree(ott_id='1066581').response_dict


    def test_synth_subtree_good_ott(self):
        res = OT.synth_subtree(ott_id='770309')
        assert isinstance(res.tree, Tree)
        


if __name__ == '__main__':
    unittest.main()
