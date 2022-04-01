# From Luna's https://github.com/LunaSare/opentree-ipynb/blob/master/py/get_subtree_for_rank.py
import os
import re
import sys
import gzip
import shutil
import copy
from opentree import OT


_DEBUG = 1
def debug(msg):
    """short debugging command
    """
    if _DEBUG == 1:
        print(msg)

def download_taxonomy_file(version, loc):
    # download ott taxonomy
    version = str(version)
    path = loc + '/' +'ott' + version
    if os.path.exists(path + '/' + 'taxonomy.tsv'):
        sys.stdout.write("Taxonomy already available at {}".format(path))
        return path
    if os.path.exists(path + '.tgz') == False: #Download the file if you don't have it
        os.system('wget "http://files.opentreeoflife.org/ott/ott{}/ott{}.tgz" -P {}'.format(version, version, loc))
    os.system("tar -xzvf {}/ott{}.tgz -C {}".format(loc, version, loc))
    assert os.path.exists(path + '/' + 'taxonomy.tsv')
    return path


def get_forwards_dict(forwards_file):
    """Returns a dictionary with new ott_ids for forwarded ott_ids
    """
    fwd_dict = {}
    fi=open(forwards_file)
    header = fi.readline()
    for lin in fi:
        lii = lin.split()
        fwd_dict[int(lii[0])]=lii[1]
    return fwd_dict

def clean_taxonomy_file(taxonomy_file):
    """Generates a pruned taxonomy.
    cleans up the word 'species' and the flag 'no rank - terminal', which is not associated to higher taxonomic ranks
    """
    taxon_dir = os.path.dirname(taxonomy_file)
    output_path = "{}/taxonomy_clean.tsv".format(taxon_dir)
    if not os.path.exists(output_path):
        # clean taxonomy file, writes cleaned file to taxonomy_clean.tsv
        os.system('grep -a -v "major_rank_conflict" ' + taxonomy_file + ' | egrep -a -v "sibling_higher" | egrep -a -v "varietas" | egrep -a -v "no rank" | egrep -a -v "Incertae" | egrep -a -v "incertae" | egrep -a -v "uncultured" | egrep -a -v "barren" | egrep -a -v "extinct" | egrep -a -v "unplaced" | egrep -a -v "hidden" | egrep -a -v "inconsistent" | egrep -a -v "synonym" > {}'.format(output_path))
    assert os.path.exists(output_path)
    return output_path


def get_ott_ids_for_rank(rank, taxonomy_file, synth_only = True):
    """Returns all the ott_ids for a given rank.
    Args
    rank: (must be in ['species', 'genus', 'family', 'order', 'class'])
    taxonomy_file: path to taxonomy.tsv

    If synth_only == True, will return only ids included in synth. 
    (Does not assess if taxa actaully appear as monophyletic in synth, e.g. if  taxa are broken.)
    """
    assert rank in ['species', 'genus', 'family', 'order', 'class']
    assert os.path.exists(taxonomy_file)
    taxon_dir = os.path.dirname(taxonomy_file)
    output_path = "{}/{}.tsv".format(taxon_dir, rank)
    #if not os.path.exists(output_path):
    os.system("""cat {tf} | awk '$7 == "{r}"' > {op}""".format(tf=taxonomy_file, r=rank, op=output_path))
        # clean taxonomy file
#        os.system('grep -a "' + rank + '" ' + taxonomy_file + ' | egrep -v "Incertae" | egrep -v "no rank" | egrep -v "major_rank_conflict" | egrep -v "uncultured" | egrep -v "barren" | egrep -v "extinct" | egrep -v "incertae" | egrep -v "unplaced" | egrep -v "hidden" | egrep -v "inconsistent"  | egrep -v "synonym" | egrep -v "in ' + rank + '" | egrep -v "species" | egrep -v "genus" | egrep -v "super' + rank + '" | egrep -v "sub' + rank + '" > {}'.format(output_path))
    # extract ott ids from taxonomy reduced file
    with open(output_path, "r") as inp:
        ott_ids = []
        for lin in inp:
            lii = lin.split('\t')
            ott_ids.append(lii[0])
    if synth_only == True:
        nodes = ['ott' + idn for idn in ott_ids]
        resp = OT.synth_node_info(node_ids = nodes)
        if 'unknown' in resp.response_dict:
            synth_ids = set(nodes).difference(set(resp.response_dict['unknown']))
            ott_ids = [nodeid.strip('ott') for nodeid in synth_ids]
    return ott_ids


def get_ott_ids_for_group(group_ott_id, write_file = 'children_ott_ids.txt', synth_only = False):
    """Returns all descendent ottids of a taxon"""
    sys.stdout.write('Gathering ott ids from group with ott id {}.\n'.format(group_ott_id))
    #debug(group_ott_id)
    subtree = OT.taxon_subtree(ott_id = group_ott_id, label_format='name_and_id')
    if synth_only == True:
        nodes = [taxon.label.split()[-1] for taxon in subtree.tree.taxon_namespace]
        resp = OT.synth_node_info(node_ids = nodes)
        if 'unknown' in resp.response_dict:
            synth_ids = set(nodes).difference(set(resp.response_dict['unknown']))
            ott_ids = [nodeid.strip('ott') for nodeid in synth_ids]
    else:
        ott_ids =[taxon.label.split()[-1].strip('ott') for taxon in subtree.tree.taxon_namespace]
    return ott_ids


def get_ott_ids_group_and_rank(group_ott_id, rank, taxonomy_file, synth_only=True):
    """Get all ott_ids of rank 'rank' in group 'group_ott_id'
    e.g. get all genera in Aves

    """
    # clean taxonomy file
    # get group ott ids
    children_ott_ids = get_ott_ids_for_group(group_ott_id)
    # get rank ott ids
    rank_ott_ids = get_ott_ids_for_rank(rank, taxonomy_file, synth_only = synth_only)
    # get rank ott ids that are in children ott ids:
    ott_ids = []
    for item in children_ott_ids:
        if item in rank_ott_ids:
            ott_ids.append(item)
    return(ott_ids)


def standardize_labels(tree, prob_char = "():#", replace_w = '_'):
    """While parens in labels is acceptable Newick, some tree viewers (e.g. itol) cannot deal
    This takes a tree and removes troublsesome characters"""
    for taxon in tree.taxon_namespace:
        taxon.label = remove_problem_characters(taxon.label, prob_char, replace_w)
    for node in tree:
        if node.label:
            node.label = remove_problem_characters(node.label, prob_char, replace_w)
    return tree

def remove_problem_characters(instr, prob_char = "():#", replace_w = ''):
    """While colons, parens, etc are leagal in newick labels, 
    many tree viewers won't read or misread trees with them.
    This function replaces problem characters in a string with a replacement char.

    Args:
        instr: The input string
        prob_char: String containing problematic characters. Default  is"():#"
        replace_w: Character to replace problem characters with. Default  is "_"

    Returns:
        String with problem characters replaced."""

    problem_characters = set(prob_char)
    for char in problem_characters:
        instr = instr.replace(char,replace_w)
    return instr

def _gather_broken_taxa_info(broken_response, label_format):
    """Gathers information about broken taxa in a synth tree call

    Args:
        broken_response: induced_subtree_response['broken']
        label format: one of ['name', 'id', 'name_and_id']

    Returns: (relabel, relabel_ott_ids, broken_dict)
        where 
        relabel: {nodeid : [label_broken_tax1, label_broken_tax2]
        relabel_ott_ids: {nodeid : [ottid_broken_tax1, ottid_broken_tax2]
        broken_dict: {ottid_broken_tax1: {'url:  url_to_taxonomy,
                                          'MRCA_location_in_synth': nodeid1,
                                          'broken_taxa_mapping_to_same_node': ottid_broken_tax2,
                                          and all the other responses from OT.taxon_info, e.g.
                                          'name': ott taxon name,
                                          }
                    }
        
    """
    broken_dict = {}
    relabel = {}
    relabel_ott_ids = {}
    for taxon in broken_response:
        remap = broken_response[taxon] # Where on the tree is that taxon now?
        ott_id = taxon.strip('ott')
        tax_inf = OT.taxon_info(ott_id=ott_id).response_dict
        tax_inf['tax_url'] = "https://tree.opentreeoflife.org/taxonomy/browse?id={}".format(ott_id)
        tax_inf['synth_url'] = "https://tree.opentreeoflife.org/opentree/argus/ottol@{}".format(ott_id)
        tax_inf['MRCA_location_in_synth'] = remap
        taxon_name = tax_inf.get('name', taxon)
        if label_format == 'name':
            taxon_label = "{}".format(taxon_name)
        elif label_format == 'name_and_id':
            taxon_label = "{}_{}".format(taxon_name, taxon)
        else:
            taxon_label = taxon
        if remap not in relabel:
            relabel[remap] = [] #Sometimes multiple taxa map to the same node or id
            relabel_ott_ids[remap] = []
        relabel[remap].append("{}".format(taxon_label))
        relabel_ott_ids[remap].append(ott_id)
        tax_inf['broken_taxa_mapping_to_same_node'] = relabel[remap]
        broken_dict[ott_id] = tax_inf
    return relabel, relabel_ott_ids, broken_dict


def _gather_unknown_taxa_info(unknown_ids):
    """Gathers taxon info for unknwon ids

    Args:
        unknown_ids: a list of unknown ott ids

    Returns a dictionary containing:
        unknown_dict: a dictionary with ott_ids as keys
            value: dictionary containnig
                full response of a taxon_info call
                + 'url': the link to the taxon in taxonomy browser

    """
    unknown_dict = {}
    for unk in unknown_ids:
            uid = unk.strip('ott') #URL for taxonomy needs integer
            tax_inf = OT.taxon_info(ott_id=uid).response_dict
            tax_inf['url'] = "https://tree.opentreeoflife.org/taxonomy/browse?id={}".format(uid)
            unknown_dict[unk] = tax_inf
    return unknown_dict

def generate_source_lookup(source_name, taxonomy_file):
    assert source_name in ['ncbi', 'gbif', 'worms', 'if', 'irmng']
    assert os.path.exists(taxonomy_file)
    lookup = {}
    for lin in taxonomy_file:
        lii = lin.split()
        ott_id = lii[0].strip()
        sources = lii[4].strip().split(',')
        match = []
        for source in sources:
            if source.startswith(source_name):
                sid = source.split(":")[1]
                match.append(sid)
        lookup[ott_id] = match
    return lookup


def labelled_induced_synth(ott_ids, label_format = 'name', inc_unlabelled_mrca=False, standardize=True):
    """Interpreting node ids from a search on taxa can be challenging.
    This relabels MRCA based tips with what broken taxa they were replacing.
    Sometimes several query taxa map to the same synth node.

    Args:
        ott_ids: The search taxa, as ott_ids. Can be integers or strings prefixed with "ott"
        label_format: One of 'name', 'id', 'name_and_id'. Default  is "name"
        inc_unlabelled_mrca: Whether to include node labels form synth that do not correspond to taxa
                             Default  is False
        standardize: Whether to standardize taxon labels by removing problem characters. Default is True

    Returns a dictionary containing:
        tree, unknown_ids
        tree: a dendropy tree object with taxa labelled acrording to 'label_format'
        unknown_ids: a list of the input ott_ids that were not found

    """
    
    # call synth tree
    curr_ids = copy.deepcopy(ott_ids) #track who we lost
    call_record = OT.ws.tree_of_life_induced_subtree(ott_ids=curr_ids,
                                                     label_format='name_and_id')#This needs to be id
    # often some ids are not found - cull but track
    if call_record.response_dict.get('unknown'):
        unknown_dict = _gather_unknown_taxa_info(call_record.response_dict['unknown'].keys())
        OT._cull_unknown_ids_from_args(call_record, node_ids=None, ott_ids=curr_ids)
        call_record = OT.ws.tree_of_life_induced_subtree(ott_ids=curr_ids,
                                                     label_format='name_and_id')
    else:
        unknown_dict = {}

    
    assert label_format in ['name', 'id', 'name_and_id'] ##this only apply's to the re-labeled output, not the first call
    relabel, relabel_ott_ids, broken_dict = _gather_broken_taxa_info(call_record.response_dict['broken'], label_format)

    labelled_tree = copy.deepcopy(call_record.tree)
    label_matches = {}
    for taxon in labelled_tree.taxon_namespace:#Are these necessarily tips???
        if taxon.label.startswith('mrca'):
            orig = taxon.label
            assert taxon.label in relabel
            for brok_taxon in relabel_ott_ids[taxon.label]:
                broken_dict[brok_taxon]['is_tip'] = True
            taxon.label = 'MRCA of taxa in '+' and '.join(relabel[taxon.label])
            label_matches[orig] = taxon.label
        else:
            orig = taxon.label
            ott_taxon_name = " ".join(taxon.label.split()[:-1])
            ott_taxon_name = remove_problem_characters(ott_taxon_name)
            ott = taxon.label.split()[-1]
            if label_format == 'name':
                new_label = ott_taxon_name
            elif label_format == 'name_and_id':
                new_label = taxon.label
            else:
                new_label = ott
            if ott in relabel:
                added_taxa = ' and MRCA of taxa in '+' and '.join(relabel[ott])
                taxon.label = new_label + added_taxa
                for brok_taxon in relabel_ott_ids[ott]:
                    broken_dict[brok_taxon]['is_tip'] = False
            else:
                taxon.label =  new_label
            label_matches[orig] = taxon.label

    for node in labelled_tree:
        if node.label and node.label != '':
            orig = node.label
            if node.taxon:
                node.label = None
            else:
                if node.label.startswith('mrca'):
                    if node.label in relabel:
                        for brok_taxon in relabel_ott_ids[node.label]:
                            broken_dict[brok_taxon]['is_tip'] = False
                        node.label = 'MRCA of taxa in '+' and '.join(relabel[node.label])
                        label_matches[orig] = node.label
                    elif inc_unlabelled_mrca:
                        label_matches[orig] = node.label
                        pass
                    else:
                        label_matches[orig] = node.label
                        node.label = None
                         
                else:
                    ott_taxon_name = " ".join(node.label.split()[:-1])
                    ott_taxon_name = remove_problem_characters(ott_taxon_name)
                    ott = node.label.split()[-1]
                    if label_format == 'name':
                        new_label = ott_taxon_name
                    elif label_format == 'name_and_id':
                        new_label = node.label
                    else:
                        new_label = ott
                    if ott in relabel:
                        added_taxa = 'MRCA of taxa in '+' and '.join(relabel[ott])
                        node.label = new_label + added_taxa
                        for brok_taxon in relabel_ott_ids[ott]:
                            broken_dict[brok_taxon]['is_tip'] = False
                    else:
                        node.label =  new_label
                    label_matches[orig] = node.label

    if standardize == True:
        labelled_tree = standardize_labels(labelled_tree)
    return {'labelled_tree':labelled_tree,
            'original_tree':call_record.tree,
            'unknown_ids':unknown_dict,
            'non-monophyletic_taxa':broken_dict,
            'supporting_studies': call_record.response_dict["supporting_studies"],
            'label_map':label_matches}



def generate_node_annotation(tree):
    """inputs:
    tree
    Tree in dendropy format. must be labelled with ott_ids
    outputs:
    dictionary with keys node_labels

    """
    node_annotation = {}
    for node in tree:
        if node.label:
            node_annotation[node.label] = {}
        elif node.taxon:
            if node.taxon.label:
                node_annotation[node.taxon.label] = {}
    for node_label in node_annotation:
        assert node_label.startswith('ott') or node_label.startswith('mrca')
        node_annotation[node_label] = {}
        node_annotation[node_label]['families'] = []
        node_annotation[node_label]['studies'] = []
        node_annotation[node_label]['strict_support'] = []
        node_annotation[node_label]['support'] = []
        node_annotation[node_label]['conflict'] = []
    node_ids = node_annotation.keys()
    resp = OT.synth_node_info(node_ids).response_dict
    node_id_resp = {}
    for node_info in resp:
        node_id_resp[node_info['node_id']] = node_info
    for node in node_annotation:
        supporting = node_id_resp[node].get('source_id_map')
        strict_support = node_id_resp[node].get('supported_by', {})
        ppo = node_id_resp[node].get('partial_path_of', {})
        conflict = node_id_resp[node].get('conflicts_with', [])
        if supporting.keys() == set(['ott3.2draft9']):
            node_annotation[node]['studies'] = 0
        else:
            node_annotation[node]['studies'] = len(supporting.keys())
        if strict_support.keys() == set(['ott3.2draft9']):
            node_annotation[node]['strict_support'] = 0
        else:
            node_annotation[node]['strict_support'] = len(strict_support.keys())
        gen_support = set(list(strict_support.keys()) + list(ppo.keys()))
        if 'ott3.2draft9' in gen_support:
            gen_support.remove('ott3.2draft9')
        node_annotation[node]['support'] = len(gen_support)
        node_annotation[node]['conflict'] = len(conflict)
    return node_annotation

def generate_tip_translation(subtree, taxonomy_file):
    """inputs:
    tree
    Tree in dendropy format. must be labelled with ott_ids
    outputs:
    dictionary mapping labels to names

    """
    assert os.path.exists(taxonomy_file)
    tip_translation = {}
    for tip in subtree.leaf_node_iter():
        tip_translation[tip.taxon.label] = ''
    for lin in open(taxonomy_file).readlines():
        lii = lin.split('\t|\t')
        if 'ott'+lii[0] in tip_translation:
            tip_translation['ott'+lii[0]] = lii[2]




def conflict_tree_str(inputtree):
    """Write out a tree string with labels that work for the OpenTree Conflict API
    """
    tmp_tree = copy.deepcopy(inputtree)
    i = 1
    for node in tmp_tree:
        i += 1
        if node.taxon:
            ottid = node.taxon.label
            new_label = "_nd{}_{}".format(i, ottid)
            node.taxon.label = new_label
        else:
            node.label = "_nd{}_".format(i)
    return tmp_tree.as_string(schema="newick")

    
#def write_itol_annotation():
