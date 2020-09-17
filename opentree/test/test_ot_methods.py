import unittest

from opentree import OT
from opentree.ws_wrapper import OTWebServicesError

study_id = 'ot_1979'
tree_id = 'tree1'
bos = 1066581
homo = 770309

class TestOT(unittest.TestCase):
    def test_synth_files(self):
        FS = OT.files_server
        scaff_tree = OT.get_subproblem_scaffold_tree('opentree12.3')
        sub_size = OT.get_subproblem_size_info('opentree12.3')


    def test_subproblems_fail(self):
        with self.assertRaises(OTWebServicesError):
            ## Bos is not in the synth tree
            sol = OT.get_subproblem_solution('opentree12.3', bos)
            sol_trees = OT.get_subproblem_trees('opentree12.3', bos)
            rev_sol = OT.get_reversed_subproblem_solution('opentree12.3', bos)

    def test_subproblems(self):
        sol = OT.get_subproblem_solution('opentree12.3', homo)
        sol_trees = OT.get_subproblem_trees('opentree12.3', homo)
        rev_sol = OT.get_reversed_subproblem_solution('opentree12.3', homo)

    def test_about(self):
        ret = OT.about()
        assert 'taxonomy_about', 'synth_tree_about' in ret

    def test_get_tree_newick(self):
        res = OT.get_tree(study_id=study_id, tree_id=tree_id, tree_format='newick')
        nwk = res.response_dict['content'].decode("utf-8")
        assert isinstance(nwk, str)


    def test_get_tree_bad_format(self):
        with self.assertRaises(ValueError):
            res = OT.get_tree(study_id=study_id, tree_id=tree_id, tree_format='newrk')

    def test_get_tree(self):
        res =  OT.get_tree(study_id=study_id, tree_id=tree_id, label_format='ot:otttaxonname',tree_format='nexus') 
        nex = res.response_dict['content'].decode("utf-8")
        assert nex.startswith("#NEXUS")

    def test_get_tree_object(self):
        res =  OT.get_tree(study_id=study_id, tree_id=tree_id, label_format='ot:ottid',tree_format='object') 
        tree_dict = res.response_dict['data']
        assert isinstance(tree_dict, dict)

    def test_get_otus(self):
        res =  OT.get_otus(study_id=study_id) 
        otu_dict = res.response_dict['otus1']['otuById']
        assert len(otu_dict) == 45

    def test_conflict(self):
        res = OT.conflict_info(study_id=study_id, tree_id=tree_id, compare_to='synth')
        assert 'node5' in res.response_dict

    def test_properties(self):
        properties = OT.studies_properties().response_dict
        assert 'ot:curatorName', 'ot:curatorName' in properties['study_properties']
        assert 'ot:ottid', 'ot:curatorName' in properties['tree_properties']

    def test_find_studies(self):
       res = OT.find_studies("Ilex", "ot:focalCladeOTTTaxonName")
       assert  "ot_1984" in [match['ot:studyId'] for match in res.response_dict["matched_studies"]]

    def test_taxon_subtree(self):
        res = OT.taxon_subtree(ott_id=bos)
        nwk = res.response_dict['newick']
        assert isinstance(nwk, str)

    def test_contexts(self):
        contexts = OT.tnrs_contexts()
        amph = OT.tnrs_infer_context(["Bufo", "Rana", "Hyla"])
        contxt  = amph.response_dict['context_name']
        assert contxt in contexts.response_dict['ANIMALS']

    def test_tnrs_match(self):
        matches = OT.tnrs_match(["Bufo", "Rana", "Hyla"])

if __name__ == '__main__':
    unittest.main()
