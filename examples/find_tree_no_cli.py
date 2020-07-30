import json
import sys
from opentree import OpenTree


OT = OpenTree()
output = OT.find_trees(search_property="ot:branchLengthMode", value="ot:time")

study_id = "ot_864"
tree_id = "tree1"

output = OT.get_tree(study_id, tree_id)
tre = output.response_dict[tree_id]
sys.stdout.write("This tree returns fine, but isn't very meaningful due to lack of otu labels:\n\n {t}\n\n".format(t=tre))

otus = OT.get_otus(study_id)
# print(otus.reponse_dict) # says obkect has no attribute 'response_dict'

output_newick = OT.get_tree(study_id, tree_id, tree_format="newick", label_format="ot:ottid", demand_success = False)
print(output_newick)

output_conflict = OT.conflict_info(study_id = 'ot_1877', tree_id= 'tree3')
output_conflict.__dict__
output_conflict.response_dict.keys()
output_conflict.response_dict["node100"]

# for keys in output_conflict.response_dict
