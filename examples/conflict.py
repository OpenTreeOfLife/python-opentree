# conflict examples
from opentree import OpenTree, object_conversion

OT = OpenTree()
DC = object_conversion.DendropyConvert()

study_id = 'ot_1877' # "ot_864"
tree_id = 'tree3' # "tree1"

output_conflict = OT.conflict_info(study_id = study_id, tree_id= tree_id)
conf_info = output_conflict.response_dict

# list the node ids of output_conflict:
conflict_nodes = [k for k in conf_info.keys()]
len(conflict_nodes) # there are 88 nodes in conflict info


# get the source tree

def get_tree_as_dendropy(study_id, tree_id):
    study = OT.get_study(study_id)
    study_nexson = study.response_dict['data']
    tree_obj = DC.tree_from_nexson(study_nexson, tree_id)
    return tree_obj

tree_obj = get_tree_as_dendropy(study_id, tree_id)
ages = tree_obj.internal_node_ages()

print("Source tree node ids and their respective ages:")
node_labels = []
node_ages = []
for node in tree_obj.internal_nodes():
    print(node.label + ", " + str(node.age))
    node_labels.append(node.label)
    node_ages.append(node.age)

source_nodes = dict(zip(node_labels, node_ages))
matching_nodes = set(conflict_nodes) & set(node_labels)
def truncate(n, decimals=0): # from here https://realpython.com/python-rounding/
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier
print("\n Nodes in source tree with conflict data:")
for m in matching_nodes:
    print(m + ", age=  " + str(truncate(source_nodes[m], 6)) + ": " + str(conf_info[m]))

print("\nThere are " + str(len(node_labels)) + " nodes in source tree '" + tree_id + "' from study '" + study_id+  "':")
print(OT.get_study(study_id).response_dict["data"]["nexml"]['^ot:studyPublicationReference'])
print("\nThere are more nodes (" + str(len(conflict_nodes)) + ") in the conflict info from this same tree.")
print("Also, not all node ids from source trees are found in conflict info. Only " +  str(len(matching_nodes)) +
" nodes from source tree are in conflict info. The tree is not included in synthesis, but these nodes correspond to the ingroup determined by the curator.")

# ott868256
