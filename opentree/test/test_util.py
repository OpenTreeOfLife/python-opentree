import unittest

from opentree import OT, util

class TestUtil(unittest.TestCase):
    def test_taxon_flag(self):
        corr_url = 'https://github.com/OpenTreeOfLife/reference-taxonomy/wiki/Taxon-flags#flags-leading-to-taxa-being-unavailable-for-tnrs'

        util.get_suppressed_taxon_flag_expl_url()



        assert util.get_suppressed_taxon_flag_expl_url() == corr_url, util.get_suppressed_taxon_flag_expl_url()


        assert util.ott_str_as_int('23') == 23

        corr_ott_link = 'https://tree.opentreeoflife.org/taxonomy/browse?id=123'
        assert util._create_link_from_node_info_conf_key_value_pair('ott', 123) == corr_ott_link

        corr_study_link = 'https://tree.opentreeoflife.org/curator/study/view/ot_1979?tab=trees&tree=tree1&node=node5'
        assert util._create_link_from_node_info_conf_key_value_pair('ot_1979@tree1', 'node5') == corr_study_link

        blob = OT.synth_node_info(node_id='mrcaott354607ott374748').response_dict
        util.write_node_info_links_to_input_trees(blob)


        blob = OT.synth_node_info(node_id='mrcaott177ott29310').response_dict
        util.write_node_info_links_to_input_trees(blob)
        

if __name__ == '__main__':
    unittest.main()
