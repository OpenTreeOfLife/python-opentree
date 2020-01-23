import json
import sys
from opentree import OpenTree


OT = OpenTree()
output = OT.find_trees(search_property="ot:branchLengthMode", value="ot:time")
print(json.dumps(output.response_dict, indent=2, sort_keys=True))

study_id = "ot_864"
tree_id = "tree1"

output = OT.get_tree(study_id, tree_id)
tre = output.response_dict[tree_id]
sys.stdout.write("This tree returns fine, but isn't very meaningful due to lack of otu labels:\n\n {t}\n\n".format(t=tre))


output = OT.get_tree(study_id, tree_id, tree_format=".tre", label_format="ot:ottid")
sys.stdout.write("The url looks fine, but the response dict can't be decoded\n")
tre = output.response_dict[tree_id]

