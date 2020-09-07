import unittest
from opentree import util

class TestUtil(unittest.TestCase):
    def test_taxon_flag(self):
        corr_url = 'https://github.com/OpenTreeOfLife/reference-taxonomy/wiki/Taxon-flags#flags-leading-to-taxa-being-unavailable-for-tnrs'
        util.get_suppressed_taxon_flag_expl_url()


if __name__ == '__main__':
    unittest.main()
