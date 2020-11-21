import unittest

from opentree import OT, object_conversion
from dendropy import Tree
DC = object_conversion.DendropyConvert()

study_id = 'ot_1979'
tree_id = 'tree1'

class TestChronoSynthDeps(unittest.TestCase):
    def test_find_chrono(self):
        output = OT.find_trees(search_property="ot:branchLengthMode", value="ot:time")
        chronograms = set()
        for study in output.response_dict["matched_studies"]:
            study_id = study['ot:studyId']
            for tree in study['matched_trees']:
                tree_id = tree['ot:treeId']
                chronograms.add('{}@{}'.format(study_id, tree_id))
        assert 'ot_1000@tree1' in chronograms
        
    def test_dp_convert(self):
        study = OT.get_study(study_id)
        study_nexson = study.response_dict['data']
        tree_obj = DC.tree_from_nexson(study_nexson, tree_id)
        assert isinstance(tree_obj, Tree)
