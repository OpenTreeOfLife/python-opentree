import unittest

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

class TestSynthNodeInfo(object):
    """docstring for TestSynthNodeInfo"""
    def test_synth_node_info(self):
        resp = OT.synth_node_info(node_id='mrcaott354607ott374748')
        assert resp.response_dict['supported_by'] == {'ot_1344@Tr105486': 'Tn16531763'}


if __name__ == '__main__':
    unittest.main()
