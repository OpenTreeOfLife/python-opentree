from opentree import OpenTree, object_conversion
OT = OpenTree()

DC = object_conversion.DendropyConvert()


study_id = 'ot_1877'


tree_id = 'tree3' # "tree1"
study = OT.get_study(study_id)
study_nexson = study.response_dict['data']


tree_obj = DC.tree_from_nexson(study_nexson, tree_id)

tree_obj.internal_node_ages()

