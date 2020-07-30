import json
from opentree import OT
# find all trees ids that are chronograms
output = OT.find_trees('ot:time', search_property = 'ot:branchLengthMode') 

tree_dict = output.response_dict

for study in tree_dict['matched_studies']:
    study_id = study['ot:studyId']
    for tree in study['matched_trees']:
        tree_id = tree['ot:treeId']
        assert(study_id == tree['ot:studyId'])
        print("Study {} tree {}".format(study_id,tree_id))
        output_tree = OT.get_tree(study_id, tree_id, tree_format="newick", label_format="ot:ottid")
        tre = output_tree.tree
        print(tre)


