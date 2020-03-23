import sys
from opentree import OpenTree, object_conversion
OT = OpenTree()

DC = object_conversion.DendropyConvert()



def get_tree(study_id, tree_id):
    study = OT.get_study(study_id)
    study_nexson = study.response_dict['data']
    tree_obj = DC.tree_from_nexson(study_nexson, tree_id)
    return tree_obj


#this works
t1 = get_tree('ot_1877', 'tree3' )
t1.internal_node_ages()
for node in t1.internal_nodes():
    print(node)
    print(node.__dict__)

#t2 = get_tree('ot_350', 'Tr53296')


