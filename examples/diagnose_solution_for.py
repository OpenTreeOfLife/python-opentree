#!/usr/bin/env python
import logging
import json
import sys
import re
from opentree import OTCommandLineTool, ott_str_as_int



def _create_link_from_node_info_conf_key_value_pair(key, value):
    if key.lower().startswith('ott'):
        value = ott_str_as_int(value)
        return "https://tree.opentreeoflife.org/taxonomy/browse?id={}".format(value)
    study_id, tree_id = key.split('@')
    node_id = str(value)
    if node_id.startswith('ott'):
        if True:
            logging.debug("node highlighting will not work for ({}, {}, {})\n".format(study_id, tree_id, node_id))
        else:
            # This node does not occur in the input tree, it is a result of exemplification...
            #   link to its parent node in the input study
            inp_tree_nexson = OT.get_tree(study_id=study_id, tree_id=tree_id)
            tax_lineage = OT.taxon_info(ott_id=ott_str_as_int(node_id), include_lineage=True)
            anc_ids = [i.ott_id for i in tax_lineage.tree.postorder_node_iter()]
            matches = []
            for leaf in inp_tree_nexson.tree.leaf_iter():
                if leaf.otu.ott_id and leaf.otu.ott_id in anc_ids:
                    matches.append((anc_ids.index, id(leaf), leaf))
            matches.sort()
            if not matches:
                logging.warning("Could not find input node for ({}, {}, {})\n".format(study_id, tree_id, node_id))
            else:
                node_id = matches[0][-1].node_id
    tmp = "https://tree.opentreeoflife.org/curator/study/view/{s}?tab=trees&tree={t}&node={n}"
    return tmp.format(s=study_id, t=tree_id, n=node_id)


def _format_link_to_input_tree(link_dict):
    lines = []
    keys = list(link_dict.keys())
    keys.sort()
    for key in keys:
        url = _create_link_from_node_info_conf_key_value_pair(key, link_dict[key])
        if key.lower().startswith('ott'):
            line = "The Open Tree taxonomy ({}): {}".format(key, url)
        else:
            line = "input phylogeny at {}".format(url)
        lines.append(line)
    return lines


def format_node_info_links_to_input_trees(blob, out=sys.stdout):
    x = blob.get('supported_by')
    if x:
        out.write("The existence of this node in the synthetic tree is supported by:\n")
        for n, line in enumerate(_format_link_to_input_tree(x)):
            out.write("  {c}: {l}\n".format(c=n+1, l=line))
    x = blob.get('partial_path_of')
    if x:
        out.write("The branch to this node in the synthetic tree is part of a path that display the node(s):\n")
        for n, line in enumerate(_format_link_to_input_tree(x)):
            out.write("  {c}: {l}\n".format(c=n+1, l=line))
    x = blob.get('resolves')
    if x:
        out.write("The branch to this node in the synthetic tree would resolve the polytomy at node(s):\n")
        for n, line in enumerate(_format_link_to_input_tree(x)):
            out.write("  {c}: {l}\n".format(c=n+1, l=line))
    x = blob.get('terminal')
    if x:
        out.write("The branch to this node in the synthetic tree is part of a terminal edge to node(s):\n")
        for n, line in enumerate(_format_link_to_input_tree(x)):
            out.write("  {c}: {l}\n".format(c=n+1, l=line))
    x = blob.get('conflicts_with')
    if x:
        out.write("The existence of this node in the synthetic tree is conflicts with:\n")
        for n, line in enumerate(_format_link_to_input_tree(x)):
            out.write("  {c}: {l}\n".format(c=n+1, l=line))


def scaffold_tree_to_ott_id_set(tree):
    return frozenset([nd.ott_id for nd in tree.postorder_node_iter() if nd.ott_id is not None])


_name_ott_id_pat = re.compile('^(.+)[ _]ott(\d+)')
def augment_nodes_with_ot_properties(tree):
    for nd in tree.postorder_node_iter():
        label = nd.taxon.label
        m = _name_ott_id_pat.match(label)
        nd.ott_name, nd.ott_id = None, None
        if m:
            nd.ott_name = m.group(1).strip()
            nd.ott_id = int(m.group(2))

if __name__ == '__main__':
    cli = OTCommandLineTool(usage='Display node info for the synthetic tree node(s) requested',
                            common_args=("ott-id",))

    OT, args = cli.parse_cli()
    ott_id = 189136 if not args.ott_id else args.ott_id
    MOCK_RUN = True
    if not MOCK_RUN:
        output = OT.synth_node_info(ott_id=ott_id, include_lineage=True)
        if not output:
            sys.exit('Call to synth_node for {} failed.\n'.format(ott_id))
        print(json.dumps(output.response_dict, indent=2, sort_keys=True))
        tip_synth_node_info = output.response_dict
        format_node_info_links_to_input_trees(output.response_dict)
        about_info = OT.about()
        synth_tree_about = about_info['synth_tree_about']
        synth_id = synth_tree_about.response_dict['synth_id']
        subproblem_scaffold = OT.get_subproblem_scaffold_tree(synth_id)
        scaf_newick = subproblem_scaffold.response.text
    else:
        tip_synth_node_info = json.load(open('./cruft/synth_node_id_response.json', 'r', encoding='utf-8'))
        synth_id = 'opentree12.3'
        scaf_newick = open('./cruft/subproblems-scaffold-only.tre', 'r', encoding='utf-8').read().strip()
    tree = OT.ws.to_object_converter.tree_from_newick(scaf_newick)
    augment_nodes_with_ot_properties(tree)
    scaffold_id_set = scaffold_tree_to_ott_id_set(tree)
    for synth_nd in tip_synth_node_info["lineage"]:
        snid = synth_nd["node_id"]
        if snid.startswith('ott'):
            sn_ott_id = ott_str_as_int(snid)
            if sn_ott_id in scaffold_id_set:
                print("subproblem: OTT={} unique_name={}".format(sn_ott_id, synth_nd["taxon"]["unique_name"]))
