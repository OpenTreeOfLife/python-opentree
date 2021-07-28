import unittest

from opentree import OT
import dendropy

bad_study_id = "pg_873"
study_id = "ot_350"
synth_spp = ['770769','638559','336228','638539','283034']
expected_tips = ['Sterculia tragacantha ott770769', 'Hildegardia barteri ott336228', 'Sterculia balanghas ott638559', 'Firmiana simplex ott283034', 'Firmiana malayana ott638539']
tax_mrca = 996482
spp_name = "Bos grunniens"
bg_tax = 381164
conf_newick_str = "(('_nd1_ott770315','_nd2_ott417950')'_nd3_','_nd4_ott158484')'_nd5';"

class TestPhyscraperDeps(unittest.TestCase):
    def test_demands_id_arg(self):
        with self.assertRaises(TypeError):
            OT.get_study()

    def test_get_study_fail(self):
        study = OT.get_study(bad_study_id)
        assert study.response_dict == {'description': 'Study #{} GET failure'.format(bad_study_id), 'error': 1}

    def test_get_study(self):
        study = OT.get_study(study_id)
        assert 'data' in study.response_dict

    def test_synth_induced(self):
        tre = OT.synth_induced_tree(ott_ids=synth_spp).tree
        leaves = [leaf.taxon.label for leaf in OT.synth_induced_tree(ott_ids=synth_spp).tree.leaf_nodes()]
        assert leaves.sort() == expected_tips.sort()
        assert isinstance(tre, dendropy.datamodel.treemodel.Tree)

    def test_taxon_subtree(self):
        resp = OT.taxon_subtree(tax_mrca)
        taxleaves = [leaf.taxon.label for leaf in resp.tree.leaf_nodes()]
        assert len(taxleaves) == 585


    def test_taxon_mrca(self):
        mrca = OT.taxon_mrca(synth_spp).response_dict['mrca']['ott_id']
        assert mrca == tax_mrca

    def test_synth_mrca(self):
        mrca_node = OT.synth_mrca(ott_ids = synth_spp).response_dict
        assert u'taxon' in mrca_node['mrca'].keys()
        tax_id = mrca_node['mrca'][u'taxon'][u'ott_id']
        assert tax_id ==  279960

    def test_get_taxon_info(self):
        call = OT.tnrs_match([spp_name], do_approximate_matching=True)
        res = call.response_dict['results'][0]
        assert res['matches'][0]['matched_name'] == 'Bos grunniens'
        assert res['matches'][0]['taxon']['ott_id'] ==  bg_tax

    def test_ottid_from_name(self):
        ottid = OT.get_ottid_from_name('Bos grunniens')
        assert ottid == bg_tax

    def test_conflict_str(self):
        resp = OT.conflict_str(conf_newick_str, 'ott').response_dict
        assert resp['nd3']['status'] == 'conflicts_with'

    def test_find_trees(self):
        phylesystem_studies_resp = OT.find_trees(bg_tax, search_property ='ot:ottId')
        matches = [study['ot:studyId'] for study in phylesystem_studies_resp.response_dict['matched_studies']]
        assert 'ot_409' in matches

if __name__ == '__main__':
    unittest.main()
