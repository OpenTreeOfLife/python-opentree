#!/usr/bin/env python
import logging
import json
import sys
import re
from opentree import OTCommandLineTool, ott_str_as_int
import dendropy



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
        if not nd.taxon:
            nd.ott_name, nd.ott_id = None, None
            continue
        label = nd.taxon.label
        m = _name_ott_id_pat.match(label)
        nd.ott_name, nd.ott_id = None, None
        if m:
            nd.ott_name = m.group(1).strip()
            nd.ott_id = int(m.group(2))

def explore_subproblem(synth_id, ott_id, synth_node_info):
    print('Subproblem OTT={} name={}'.format(ott_id, synth_node_info["taxon"]["unique_name"]))
    ssds, ssdti = subprob_size_dict['subproblems'], subprob_size_dict['tree_ids']
    num_leaves, num_leaves_in_synth, tree_info_list = ssds['ott{}'.format(ott_id)]
    print('{} leaves in the exemplified subproblem\n'.format(num_leaves))
    print('{} leaves descended from this subproblem in the synthetic tree\n'.format(num_leaves_in_synth))
    print('Ranked input trees:\n')
    nontriv_templ = ' #{i}: NONTRIVIAL with {l} tips, and {c} splits, tree: "https://tree.opentreeoflife.org/curator/study/view/{s}?tab=trees&tree={t}'
    triv_templ = ' #{i}: trivial with {l} tips, and {c} splits, tree: "https://tree.opentreeoflife.org/curator/study/view/{s}?tab=trees&tree={t}'
    triv_tax_templ = ' #{i}: with {l} tips, and {c} splits: the OTT taxonomy provides no structure to this subproblem'
    nontriv_tax_templ = ' #{i}: with {l} tips, and {c} splits: the OTT taxonomy'
    nontriv_indices = []
    for n, el in enumerate(tree_info_list):
        num_tips, num_splits, tree_id_idx = el
        study_at_tree_dot_tree = ssdti[tree_id_idx]
        if num_splits > 0:
            nontriv_indices.append(n)
        if study_at_tree_dot_tree != 'TAXONOMY':
            assert study_at_tree_dot_tree.endswith('.tre')
            study_at_tree = study_at_tree_dot_tree[:-4]
            study_id, tree_id = study_at_tree.split('@')
            templ = nontriv_templ if num_splits > 0 else triv_templ
            print(templ.format(i=1+n, l=num_tips, c=num_splits, s=study_id, t=tree_id))
        else:
            templ = nontriv_tax_templ if num_splits > 0 else triv_tax_templ
            print(templ.format(i=1+n, l=num_tips, c=num_splits))
    concat_newick = OT.get_subproblem_trees(synth_id, ott_id).response.text
    newick_list = [i for i in concat_newick.split('\n') if i.strip()]
    if len(newick_list) != len(tree_info_list):
        x = "Subproblem had {} newicks, when only {} were expected. Tree indices may be off!"
        logging.warning(x.format(len(newick_list), len(tree_info_list)))
    soln_newick = OT.get_subproblem_solution(synth_id, ott_id).response.text
    rev_soln_newick = OT.get_reversed_subproblem_solution(synth_id, ott_id).response.text
    newick_list.extend([soln_newick, rev_soln_newick])
    tree_obj_list = OT.ws.to_object_converter.tree_list_from_newicks(newick_list, rooting='force-rooted')
    tree1, tree2 = tree_obj_list[-2:]
    rf = dendropy.calculate.treecompare.symmetric_difference(tree1, tree2, is_bipartitions_updated=False)
    print("Synthetic tree's subproblem solution:")
    print(tree1.as_ascii_plot())
    print("Synthetic tree's subproblem solution if tree ranks were reversed:")
    print(tree2.as_ascii_plot())
    print('RF symmetric distance between OT backbone and the tree from reversing phylo rankings = {}'.format(rf))
    if rf > 0:
        contree = tree_obj_list.consensus()
        print("Majority-rule consensus of those 2 trees:")
        print(contree.as_ascii_plot())


def prompt_for_subproblem_exploration(synth_id, subproblem_list):
    while True:
        print("This taxon's position is determined by the resolution of the following subproblems:")
        for index, group in enumerate(subproblem_list):
            print('  #{}: {}'.format(1+index, group[0]))
        resp = input("Enter a number to explore a subproblem (return to exit): ")
        if not resp.strip():
            return
        try:
            choice = int(resp.strip()) - 1
            chosen_el = subproblem_list[choice]
        except:
            sys.stderr.write('Expected a number enter control-D or simply Return to exit.\n')
        else:
            explore_subproblem(synth_id, chosen_el[1], chosen_el[2])



if __name__ == '__main__':
    cli = OTCommandLineTool(usage='Display node info for the synthetic tree node(s) requested',
                            common_args=("ott-id",))

    OT, args = cli.parse_cli()
    ott_id = 189136 if not args.ott_id else args.ott_idsynth_id
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
        subprob_size_dict = OT.get_subproblem_size_info(synth_id).response_dict
    else:
        tip_synth_node_info = json.load(open('./cruft/synth_node_id_response.json', 'r', encoding='utf-8'))
        synth_id = 'opentree12.3'
        scaf_newick = open('./cruft/subproblems-scaffold-only.tre', 'r', encoding='utf-8').read().strip()
        subprob_size_dict = json.load(open('./cruft/subproblem_size_summary.json', 'r', encoding='utf-8'))
    tree = OT.ws.to_object_converter.tree_from_newick(scaf_newick)
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
    prompt_for_subproblem_exploration(synth_id, subproblem_list)