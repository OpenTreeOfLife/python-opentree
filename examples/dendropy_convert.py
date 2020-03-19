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


#this doesn't
t2 = get_tree('ot_350', 'Tr53297')

'''Traceback (most recent call last):
  File "<stdin>", line 2, in <module>
  File "<stdin>", line 4, in node_ages
  File "/home/ejmctavish/projects/otapi/python-opentree/opentree/object_conversion.py", line 67, in tree_from_nexson
    raise ValueError('expecting just  "otuById" in OTUs object')
ValueError: expecting just  "otuById" in OTUs object
'''

