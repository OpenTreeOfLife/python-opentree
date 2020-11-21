#!/usr/bin/env python3
"""Miscellaneous light-weight functions for common operations when working with Open Tree data"""
import logging
import sys

_TAXONOMY_WIKI_URL = "https://github.com/OpenTreeOfLife/reference-taxonomy/wiki"
_TAXON_FLAGS_WIKI_URL = "{}/Taxon-flags".format(_TAXONOMY_WIKI_URL)
_SUPPRESSED_TAXON_FLAGS_WIKI_URL = _TAXON_FLAGS_WIKI_URL + '#flags-leading-to-taxa-being-unavailable-for-tnrs'


def get_suppressed_taxon_flag_expl_url():
    """Returns the current URL describing taxon flags that lead to suppression"""
    return _SUPPRESSED_TAXON_FLAGS_WIKI_URL


def ott_str_as_int(o):
    """Returns the OTT Id `o` as an integer if `o` is an integer or a string starting with ott (case-insensitive).

    Raises a ValueError if the string does not match ^(OTT)?[0-9]+$
    """
    if isinstance(o, int):
        return o
    if o.startswith('ott'):
        return int(o[3:])
    try:
        return int(o)
    except:
        if o.lower().startswith('ott'):
            return int(o[3:])
        raise


def _create_link_from_node_info_conf_key_value_pair(key, value):
    """Takes the key value pairs contained in the ToL/node_info call and returns a URL for the node"""
    if key.lower().startswith('ott'):
        value = ott_str_as_int(value)
        return "https://tree.opentreeoflife.org/taxonomy/browse?id={}".format(value)
    study_id, tree_id = key.split('@')
    node_id = str(value)
    if node_id.startswith('ott'): ##todo Check if link is possible
        logging.debug("node highlighting will not work for ({}, {}, {})\n".format(study_id, tree_id, node_id))
        # # This node does not occur in the input tree, it is a result of exemplification...
        # #   link to its parent node in the input study
        # inp_tree_nexson = OT.get_tree(study_id=study_id, tree_id=tree_id)
        # tax_lineage = OT.taxon_info(ott_id=ott_str_as_int(node_id), include_lineage=True)
        # anc_ids = [i.ott_id for i in tax_lineage.tree.postorder_node_iter()]
        # matches = []
        # for leaf in inp_tree_nexson.tree.leaf_node_iter():
        #     if leaf.otu.ott_id and leaf.otu.ott_id in anc_ids:
        #         matches.append((anc_ids.index, id(leaf), leaf))
        # matches.sort()
        # if not matches:
        #     logging.warning("Could not find input node for ({}, {}, {})\n".format(study_id, tree_id, node_id))
        # else:
        #     node_id = matches[0][-1].node_id
        #
    tmp = "https://tree.opentreeoflife.org/curator/study/view/{s}?tab=trees&tree={t}&node={n}"
    return tmp.format(s=study_id, t=tree_id, n=node_id)


def _format_link_to_input_tree(link_dict):
    """Returns a list of lines with node links. `link_dict` that is from a ToL/node_info response's support fields"""
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


def write_node_info_links_to_input_trees(blob, out=sys.stdout):
    """Writes a summary of the support/conflict info from a ToL/node_info call response `blob` to stream `out`"""
    x = blob.get('supported_by')
    if x:
        out.write("The existence of this node in the synthetic tree is supported by:\n")
        for n, line in enumerate(_format_link_to_input_tree(x)):
            out.write(" {c:3d}: {l}\n".format(c=n + 1, l=line))
    x = blob.get('partial_path_of')
    if x:
        out.write("The branch to this node in the synthetic tree is part of a path that display the node(s):\n")
        for n, line in enumerate(_format_link_to_input_tree(x)):
            out.write(" {c:3d}: {l}\n".format(c=n + 1, l=line))
    x = blob.get('resolves')
    if x:
        out.write("The branch to this node in the synthetic tree would resolve the polytomy at node(s):\n")
        for n, line in enumerate(_format_link_to_input_tree(x)):
            out.write(" {c:3d}: {l}\n".format(c=n + 1, l=line))
    x = blob.get('terminal')
    if x:
        out.write("The branch to this node in the synthetic tree is part of a terminal edge to node(s):\n")
        for n, line in enumerate(_format_link_to_input_tree(x)):
            out.write(" {c:3d}: {l}\n".format(c=n + 1, l=line))
    x = blob.get('conflicts_with')
    if x:
        out.write("The existence of this node in the synthetic tree is conflicts with:\n")
        for n, line in enumerate(_format_link_to_input_tree(x)):
            out.write(" {c:3d}: {l}\n".format(c=n + 1, l=line))

