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

tre2 = output._response_obj.text
sys.stdout.write("ahhh is issue converting from byte string, works if you get as text \n{}\n".format(tre2))



sys.stdout.write("The response dict can't be decoded as json\n")
tre = output.response_dict[tree_id]

