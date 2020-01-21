import json
from opentree import OT

output = OT.find_trees(search_property="ot:branchLengthMode", value="ot:time")
print(json.dumps(output.response_dict, indent=2, sort_keys=True))

