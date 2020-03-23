from opentree import OpenTree, object_conversion
OT = OpenTree()

DC = object_conversion.DendropyConvert()


study_id = 'ot_1877'
study = OT.get_study(study_id)
study_nexson = study.response_dict['data']
study_nexson["nexml"].keys()
tree_id = 'tree3' # "tree1"
tree_obj = DC.tree_from_nexson(study_nexson, tree_id)

tree_obj.internal_node_ages()

tree_obj.internal_nodes()
