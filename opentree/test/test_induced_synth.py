import unittest

from opentree import OT

class TestInducedSynth(unittest.TestCase):
    def test_demands_id_arg(self):
        with self.assertRaises(ValueError):
            OT.induced_synth_tree()

    def test_int_ott_ids(self):
        with self.assertRaises(ValueError):
            OT.induced_synth_tree(ott_ids=["hi"])


if __name__ == '__main__':
    unittest.main()
