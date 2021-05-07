#!/usr/bin/env python
"""Allows you to investigate the phylogenetic inputs, and subproblems traversing node in the synthetioc tree.
e.g., for the genus 'Bos' 
python examples/diagnose_solution_for.py --ott-id 1066581"""
import logging
import re
import sys
import json

import dendropy

from opentree import OTCommandLineTool, ott_str_as_int, write_node_info_links_to_input_trees


def scaffold_tree_to_ott_id_set(tree):
    return frozenset([nd.ott_id for nd in tree.postorder_node_iter() if nd.ott_id is not None])


_name_ott_id_pat = re.compile(r'^(.+)[ _]ott(\d+)')


def augment_nodes_with_ot_properties_and_find_subproblems(tree, find_node):
    for nd in tree.postorder_node_iter():
        if not nd.taxon:
            nd.ott_name, nd.ott_id = None, None
            continue
        label = nd.taxon.label
        m = _name_ott_id_pat.match(label)
        nd.ott_name, nd.ott_id = None, None
        if m:
            nd.ott_name = m.group(1).strip()
            nd.ott_id = int(m.group(2))
            if nd.ott_id == find_node:
                return nd


def main(args):
    if not args.ott_id:
        sys.exit('The --ott-id argument is mandatory.\n')
    ott_id = int(args.ott_id)
    about_info = OT.about(include_source_list=True)
    synth_tree_about = about_info['synth_tree_about']
    input_tree_list = synth_tree_about['source_list']
    synth_id = synth_tree_about['synth_id']
    subproblem_scaffold = OT.get_subproblem_scaffold_tree(synth_id)
    scaf_newick = subproblem_scaffold.response.text
    scaf_tree = OT.ws.to_object_converter.tree_from_newick(scaf_newick)
    nd = augment_nodes_with_ot_properties_and_find_subproblems(scaf_tree, ott_id)
    subtree_nds_ott_ids = [n.ott_id for n in nd.preorder_iter()]
    inputs = set()
    sys.stderr.write(' {} subproblems descend from {}\n'.format(len(subtree_nds_ott_ids), ott_id))
    for n, o in enumerate(subtree_nds_ott_ids):
        sys.stderr.write(' Fetching tree names for ott{} the {}/{} subproblem to fetch\n'.format(o, n+1, len(subtree_nds_ott_ids)))
        r = OT.get_subproblem_tree_names(synth_id=synth_id, ott_id=o)
        inputs.update(r.response_decoded)
    subproblem_size_dict = OT.get_subproblem_size_info(synth_id).response_dict
    for it in input_tree_list:
        dec = it + ".tre"
        if dec in inputs:
            print(it)
    return
    subproblems = set(subproblem_size_dict["subproblems"])
    print(subproblems)
    return
    output = OT.get_subproblem_tree_names(synth_id=synth_id, ott_id=ott_id)
    if not output:
        sys.exit('Call to synth_node for {} failed.\n'.format(ott_id))
    print(output.response_decoded)
    return
    subprob_size_dict = OT.get_subproblem_size_info(synth_id).response_dict
    augment_nodes_with_ot_properties(tree)
    scaffold_id_set = scaffold_tree_to_ott_id_set(tree)
    subproblem_list = []
    for synth_nd in tip_synth_node_info["lineage"]:
        snid = synth_nd["node_id"]
        if snid.startswith('ott'):
            sn_ott_id = ott_str_as_int(snid)
            if sn_ott_id in scaffold_id_set:
                m = "subproblem: OTT={} unique_name={}".format(sn_ott_id, synth_nd["taxon"]["unique_name"])
                subproblem_list.append((m, sn_ott_id, synth_nd))
    subproblem_list.reverse()
    prompt_for_subproblem_exploration(synth_id, subproblem_list, subprob_size_dict)


if __name__ == '__main__':
    cli = OTCommandLineTool(usage='List all of the trees that were used in subproblems that descend from a particular node',
                            common_args=("ott-id",))

    OT, parsed_args = cli.parse_cli()
    main(parsed_args)
