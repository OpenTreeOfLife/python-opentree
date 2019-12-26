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
        call_record = OT.synth_induced_tree(ott_ids=[417950, 770315])
        print(call_record.tree)

    def test_success_node_ids(self):
        call_record = OT.synth_induced_tree(node_ids=['ott417950', 'ott770315'])
        print(call_record.tree)

    def test_success_mixed_ids(self):
        call_record = OT.synth_induced_tree(node_ids=['ott770315'], ott_ids=[417950])
        print(call_record.tree)


if __name__ == '__main__':
    unittest.main()
