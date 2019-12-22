#!/usr/bin/env python3

import dendropy


def get_object_converter(object_conversion_schema):
    if object_conversion_schema.lower() == 'dendropy':
        return DendropyConvert()
    raise ValueError('Currently only conversion to DendroPy objects is supported.')


# noinspection PyMethodMayBeStatic
class DendropyConvert(object):
    def tree_from_newick(self, newick, suppress_internal_node_taxa=False):
        return dendropy.Tree.get(data=newick, schema="newick", suppress_internal_node_taxa=suppress_internal_node_taxa)
