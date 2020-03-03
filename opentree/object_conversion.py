#!/usr/bin/env python3

import dendropy
import re

def get_object_converter(object_conversion_schema):
    if object_conversion_schema.lower() == 'dendropy':
        return DendropyConvert()
    raise ValueError('Currently only conversion to DendroPy objects is supported.')

_name_gap_ott_num = re.compile(r'^(.+)[ _]ott(\d+)$')

def _decorate_taxa_in_taxon_namespace_by_parsing_labels(tree):
    taxon_namespace = tree.taxon_namespace
    for taxon in taxon_namespace:
        label = taxon.label
        m = _name_gap_ott_num.match(label)
        if m:
            name = m.group(1).strip()
            if name and not hasattr(taxon, 'ott_taxon_name'):
                taxon.ott_taxon_name = name
            if not hasattr(taxon, 'ott_id'):
                taxon.ott_id = int(m.group(2))


# noinspection PyMethodMayBeStatic
class DendropyConvert(object):
    """
    Class to convert newicks to dendropy objects
    """
    def tree_from_newick(self, newick, suppress_internal_node_taxa=False, **kwargs):
        tree = dendropy.Tree.get(data=newick, schema="newick",
                                 suppress_internal_node_taxa=suppress_internal_node_taxa, **kwargs)
        _decorate_taxa_in_taxon_namespace_by_parsing_labels(tree)
        return tree

    def tree_list_from_newicks(self, newick_list, suppress_internal_node_taxa=False, **kwargs):
        concat = '\n'.join(newick_list)
        tree_list = dendropy.TreeList.get(data=concat,
                                          schema="newick",
                                          suppress_internal_node_taxa=suppress_internal_node_taxa,
                                          **kwargs)
        _decorate_taxa_in_taxon_namespace_by_parsing_labels(tree_list)
        return tree_list

    def taxon_namespace_and_id_dict_from_nexson_otus_obj(self, otus_obj, otus_id):
        tn = dendropy.TaxonNamespace(label=otus_id)
        id_to_taxon = {}
        for oid, otu_obj in otus_obj.items():
            dt = tn.new_taxon(oid)
            if oid in id_to_taxon:
                raise ValueError('otu id "{}" repeated'.format(oid))
            id_to_taxon[oid] = dt
            dt.ott_taxon_name, dt.ott_id, dt.original_label = None, None, None
            for meta_key, meta_v in otu_obj.items():
                if meta_key == '^ot:ottTaxonName':
                    dt.ott_taxon_name = meta_v
                elif meta_key == '^ot:originalLabel':
                    dt.original_label = meta_v
                elif meta_key == '^ot:ottId':
                    dt.ott_id = meta_v
        return tn, id_to_taxon

    def tree_from_nexson(self, nexson, tree_id, label_format="ot:originallabel"):
        to_taxon_attr = {
            "ot:originallabel": "original_label",
            "ot:ottid": "ott_id",
            "ot:otttaxonname": "ott_taxon_name",
        }
        taxon_attr = to_taxon_attr[label_format.lower()]
        nexml = nexson['nexml']
        trees_sets_by_id = nexml.get('treesById', {})
        otu_set_id, tree_obj = None, None
        for tree_set_id, tree_set in trees_sets_by_id.items():
            otu_set_id = tree_set.get('@otus')
            tbi = tree_set.get('treeById', {})
            tree_obj = tbi.get(tree_id)
            if tree_obj:
                break
        if tree_obj is None:
            raise KeyError('Tree with id "{}" not found in NexSON'.format(tree_id))
        if otu_set_id is None:
            raise KeyError('Tree set missing "@otus" property')
        otus_by_id = nexml['otusById']
        otu_set = otus_by_id[otu_set_id]
        if len(otu_set) != 1:
            raise ValueError('expecting just  "otuById" in OTUs object')
        obi = otu_set["otuById"]
        tn, id2taxon = self.taxon_namespace_and_id_dict_from_nexson_otus_obj(obi, otu_set_id)
        for taxon in tn:
            tl = getattr(taxon, taxon_attr, None)
            if tl is not None:
                taxon.label = tl
        tree = dendropy.Tree(label=tree_obj.get('@label', tree_id), taxon_namespace=tn)
        tt = tree_obj["@xsi:type"]
        if tt == 'nex:FloatTree':
            tree.length_type = float
        root_node_id = tree_obj["^ot:rootNodeId"]
        spec_root_id = tree_obj["^ot:specifiedRoot"]
        if spec_root_id:
            assert spec_root_id == root_node_id
        ingroup_node_id = tree_obj.get("^ot:inGroupClade")
        non_annotations = frozenset(["^ot:inGroupClade", "^ot:rootNodeId", "^ot:specifiedRoot"])
        for key, value in tree_obj.items():
            if key in non_annotations:
                continue
            if key.startswith('^ot:'):
                tree.annotations.add_new(name=key[4:], value=value)
        nex_nds = tree_obj['nodeById']
        edges_by_src = tree_obj['edgeBySourceId']
        nd_id2dend = {}
        nexson_nd = nex_nds[root_node_id]
        _proc_nd(tree.seed_node, nexson_nd, id2taxon, root_node_id, nd_id2dend)
        to_proc = [tree.seed_node]
        while to_proc:
            next_nd = to_proc.pop(0)
            edges_dict = edges_by_src.get(next_nd.id, {})
            for edge_id, e_dict in edges_dict.items():
                new_nd = tree.node_factory()
                assert e_dict['@source'] == next_nd.id
                dest_id = e_dict['@target']
                _proc_nd(new_nd, nex_nds[dest_id], id2taxon, dest_id, nd_id2dend)
                next_nd.add_child(new_nd)
                edge_len = e_dict.get('@length')
                new_nd.edge.id = edge_id
                if edge_len is not None:
                    new_nd.edge.length = edge_len
                to_proc.append(new_nd)
        return tree

def _proc_nd(node, nexson_nd, id2taxon, node_id, nd_id2dend):
    node.id = node_id
    nd_id2dend[node_id] = node
    _decorate_nd(node, nexson_nd, id2taxon)

def _decorate_nd(node, nexson_nd, id2taxon):
    otu_id = nexson_nd.get('@otu')
    if otu_id:
        node.taxon = id2taxon[otu_id]