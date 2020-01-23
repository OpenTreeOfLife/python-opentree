import json
from opentree import OpenTree


OT = OpenTree()
output = OT.find_trees(search_property="ot:branchLengthMode", value="ot:time")
print(json.dumps(output.response_dict, indent=2, sort_keys=True))

study_id = "ot_864"
tree_id = "tree1"
output = OT.get_tree(study_id, tree_id, tree_format=".tre", label_format="ot:ottid")
tre = output.response_dict[tree_id]
print(tre)

## Compare to Dev

#devot = OpenTree(api_endpoint="dev")
#devout = devot.find_trees(search_property="ot:branchLengthMode", value="ot:time")

##compare results or whatever
