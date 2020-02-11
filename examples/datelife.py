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
print(output_conflict.response_dict["node100"])

conf_info = output_conflict.response_dict

# possible statuses are {'resolved_by', 'conflicts_with', 'supported_by', 'terminal', 'partial_path_of'}
#>>> statuses = set()
#>>> for node in conf_info:
#...     statuses.add(conf_info[node]['status'])


# step 1
# get the source nodes supporting syntethetic tree nodes:
for node in conf_info:
    status = conf_info[node]['status'] # gets the status of each node, see possibilities above
    witness = conf_info[node].get('witness', None) # gets the synthetic node id that is related to the source node
    if status == 'supported_by':
        print("{} {} {} maps to {}".format(study_id, tree_id, node, witness))

# step 2
# Get ages for those nodes

# We need either:
# - a newick tree with branch lengths whose node labels match node ids from nexson schema.
## Do peyotl schemas go from nexson tree with branch lengths to newick with branch lengths?
## Would this process retain node labels from nexson into newick?

# - a way to get node height from a nexson object.
## Maybe via Dendropy traversal of nexml/nexson tree
## this might work:
## https://dendropy.org/library/treemodel.html?highlight=ages#dendropy.datamodel.treemodel.Tree.internal_node_ages
##
import dendropy
dendropy.datamodel.treemodel.Tree.internal_node_ages

t1 = dendropy.datamodel.treemodel.Tree()
t1.__dict__
s = t1.as_string("nexml")
s.__dict__ # has no attribute __dict__

## seems that we need to go from nexson to nexml first in order to use dendropy for tree traversal.


# step 3
# make an API
# expose this info on the otol website
