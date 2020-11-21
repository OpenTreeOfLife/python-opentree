#!/usr/bin/env python
"""Allows you to investigate the phylogenetic inputs, and subproblems traversing node in the synthetioc tree.
e.g., for the genus 'Bos' 
python examples/diagnose_solution_for.py --ott-id 1066581"""
import logging
import re
import sys

import dendropy

from opentree import OTCommandLineTool, ott_str_as_int, write_node_info_links_to_input_trees


def scaffold_tree_to_ott_id_set(tree):
    return frozenset([nd.ott_id for nd in tree.postorder_node_iter() if nd.ott_id is not None])


_name_ott_id_pat = re.compile(r'^(.+)[ _]ott(\d+)')


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


def explore_subproblem(synth_id, ott_id, synth_node_info, subprob_size_dict):
    print('\n\nSubproblem OTT={} name={}'.format(ott_id, synth_node_info["taxon"]["unique_name"]))
    ssds, ssdti = subprob_size_dict['subproblems'], subprob_size_dict['tree_ids']
    num_leaves, num_leaves_in_synth, tree_info_list = ssds['ott{}'.format(ott_id)]
    print('{} leaves in the exemplified subproblem\n'.format(num_leaves))
    print('{} leaves descended from this subproblem in the synthetic tree\n'.format(num_leaves_in_synth))
    print('Ranked input trees:\n')
    study_tree_url_template = "https://tree.opentreeoflife.org/curator/study/view/{s}?tab=trees&tree={t}"
    nontriv_templ = ' #{i:3d}: NONTRIVIAL with {l} tips, and {c} splits, tree: ' + study_tree_url_template
    triv_templ = ' #{i:3d}: trivial with {l} tips, and {c} splits, tree: ' + study_tree_url_template
    triv_tax_templ = ' #{i:3d}: with {l} tips, and {c} splits: the OTT taxonomy provides no splits to this subproblem'
    nontriv_tax_templ = ' #{i:3d}: with {l} tips, and {c} splits: the OTT taxonomy'
    nontriv_indices = []
    tree_labels = []
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
            ltp = templ.format(i=1 + n, l=num_tips, c=num_splits, s=study_id, t=tree_id)
        else:
            templ = nontriv_tax_templ if num_splits > 0 else triv_tax_templ
            ltp = templ.format(i=1 + n, l=num_tips, c=num_splits)
        tree_labels.append(ltp)
        print(ltp)
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
    # noinspection PyUnresolvedReferences
    rf = dendropy.calculate.treecompare.symmetric_difference(tree1, tree2, is_bipartitions_updated=False)

    ott_id_strings = [i.label for i in tree_obj_list.taxon_namespace]
    ott_id_list = [ott_str_as_int(i) for i in ott_id_strings]
    induced = OT.synth_induced_tree(ott_ids=ott_id_list)
    o2n = {}
    for nd in induced.tree.leaf_node_iter():
        m = _name_ott_id_pat.match(nd.taxon.label)
        if m:
            name = m.group(1)
            ott_str = 'ott{}'.format(m.group(2))
            o2n[ott_str] = name
    for i in tree_obj_list.taxon_namespace:
        n = o2n.get(i.label)
        if n:
            i.label = '{} {}'.format(n, str(i.label))

    print("There are {} inputs that inform this subproblem:".format(len(nontriv_indices)))
    for ntn, ind in enumerate(nontriv_indices):
        print('Informative input #{} is tree ranked {}'.format(1 + ntn, tree_labels[ind]))
        prompt = 'Would you like to see the tree? (y/n) '
        ans = input(prompt)
        if ans.lower().startswith('y'):
            print(tree_obj_list[ind].as_ascii_plot())
    print("Synthetic tree's subproblem solution:")
    print(tree1.as_ascii_plot())
    print("Synthetic tree's subproblem solution if tree ranks were reversed:")
    print(tree2.as_ascii_plot())
    print('RF symmetric distance between OT backbone and the tree from reversing phylo rankings = {}'.format(rf))
    if rf > 0:
        contree = tree_obj_list.consensus(min_freq=.3)
        print("Majority-rule consensus of those 2 trees:")
        print(contree.as_ascii_plot())


def prompt_for_subproblem_exploration(synth_id, subproblem_list, subprob_size_dict):
    while True:
        print("\nThis taxon's position is determined by the resolution of the following subproblems:")
        for index, group in enumerate(subproblem_list):
            print('  #{:3d}: {}'.format(1 + index, group[0]))
        resp = input("\nEnter a number to explore a subproblem (return to exit): ")
        if not resp.strip():
            return
        try:
            choice = int(resp.strip()) - 1
            chosen_el = subproblem_list[choice]
        except:
            sys.stderr.write('Expected a number enter control-D or simply Return to exit.\n')
        else:
            explore_subproblem(synth_id, chosen_el[1], chosen_el[2], subprob_size_dict)


def main(args):
    if not args.ott_id:
        sys.exit('The --ott-id argument is mandatory.\n')
    ott_id = args.ott_id
    output = OT.synth_node_info(ott_id=ott_id, include_lineage=True)
    if not output:
        sys.exit('Call to synth_node for {} failed.\n'.format(ott_id))
    tip_synth_node_info = output.response_dict
    write_node_info_links_to_input_trees(output.response_dict)
    about_info = OT.about()
    synth_tree_about = about_info['synth_tree_about']
    synth_id = synth_tree_about['synth_id']
    subproblem_scaffold = OT.get_subproblem_scaffold_tree(synth_id)
    scaf_newick = subproblem_scaffold.response.text
    subprob_size_dict = OT.get_subproblem_size_info(synth_id).response_dict
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
    prompt_for_subproblem_exploration(synth_id, subproblem_list, subprob_size_dict)


if __name__ == '__main__':
    cli = OTCommandLineTool(usage='Display node info for the synthetic tree node(s) requested',
                            common_args=("ott-id",))

    OT, parsed_args = cli.parse_cli()
    main(parsed_args)
