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
    path = loc + '/' +'ott' + version
    if os.path.exists(path + '/' + 'taxonomy.tsv'):
        sys.stdout.write("Taxonomy already available at {}".format(path))
        return path
    if os.path.exists(path + '.tgz') == False: #Download the file if you don't have it
        os.system('wget "http://files.opentreeoflife.org/ott/ott{}/ott{}.tgz" -P {}'.format(version, version, loc))
    os.system("tar -xzvf {}/ott3.2.tgz -C {}".format(loc, loc))
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
    """Geneartes a pruned taxonomy.
    cleans up the word 'species' and the flag 'no rank - terminal', which is not associated to higher taxonomic ranks
    """
    taxon_dir = os.path.dirname(taxonomy_file)
    output_path = "{}/taxonomy_clean.tsv".format(taxon_dir)
    if not os.path.exists(output_path):
        # clean taxonomy file, writes cleaned file to taxonomy_clean.tsv
        os.system('grep -a -v "major_rank_conflict" ' + taxonomy_file + ' | egrep -a -v "sibling_higher" | egrep -a -v "varietas" | egrep -a -v "no rank" | egrep -a -v "Incertae" | egrep -a -v "incertae" | egrep -a -v "uncultured" | egrep -a -v "barren" | egrep -a -v "extinct" | egrep -a -v "unplaced" | egrep -a -v "hidden" | egrep -a -v "inconsistent" | egrep -a -v "synonym" > {}'.format(output_path))
    assert os.path.exists(output_path)
    return output_path


def get_ott_ids_for_rank(rank, taxonomy_file):
    """Returns all the ott_ids for a given rank.
    Args
    rank: (must be in ['species', 'genus', 'family', 'order', 'class'])
    taxonomy_file: path to taxonomy.tsv
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
    fi = open(output_path).readlines()
    ott_ids = []
    for lin in fi:
        lii = lin.split('\t')
        ott_ids.append(lii[0])
    return ott_ids


def get_ott_ids_for_group(group_ott_id, write_file = 'children_ott_ids.txt'):
    """Returns all descendent ottids of a taxon"""
    sys.stdout.write('Gathering ott ids from group with ott id {}...\n'.format(group_ott_id))
    debug(group_ott_id)
    subtree = OT.taxon_subtree(ott_id = group_ott_id, label_format='name_and_id')
    ott_ids =[taxon.label.split()[-1].strip('ott') for taxon in subtree.tree.taxon_namespace]
    return ott_ids


def get_ott_ids_group_and_rank(group_ott_id, rank, taxonomy_file):
    """Get all ott_ids of rank 'rank' in group 'group_ott_id'
    e.g. get all genera in Aves

    """
    # clean taxonomy file
    # get group ott ids
    children_ott_ids = get_ott_ids_for_group(group_ott_id)
    # get rank ott ids
    rank_ott_ids = get_ott_ids_for_rank(rank, taxonomy_file)
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

def remove_problem_characters(instr, prob_char = "():#", replace_w = '_'):
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
    broken_dict = {}
    relabel = {}
    relabel_ott_ids = {}
    for taxon in broken_response:
        remap = broken_response[taxon] # Where on the tree is that taxon now?
        ott_id = taxon.strip('ott')
        tax_inf = OT.taxon_info(ott_id=ott_id).response_dict
        tax_inf['url'] = "https://tree.opentreeoflife.org/taxonomy/browse?id={}".format(ott_id)
        tax_inf['MRCA_location_in_synth'] = remap
        taxon_name = tax_inf.get('name', taxon)
        if label_format == 'name':
            taxon_label = "{}_{}".format(taxon_name, taxon)
        elif label_format == 'name_and_id':
            taxon_label = "{}_{}".format(taxon_name, taxon)
        else:
            taxon_label = taxon
        if remap not in relabel:
            relabel[remap] = [] #Sometimes multiple taxa map to the same node or id
            relabel_ott_ids[remap] = []
        relabel[remap].append("{}".format(taxon_label))
        relabel_ott_ids[remap].append(ott_id)
        tax_inf['all_taxa_mapping_to_same_node'] = relabel[remap]
        broken_dict[ott_id] = tax_inf
    return relabel, relabel_ott_ids, broken_dict

def synth_label_broken_taxa(ott_ids, label_format = 'name', inc_unlabelled_mrca=False, standardize=True):
    """Interpreting node ids from a search on taxa can be challenging.
    This relabels MRCA based tips with what broken taxa they were replacing.
    Sometimes several query taxa map to the same synth node.

    Args:
        ott_ids: The search taxa, as ott_ids. Can be integers or strings prefixed with "ott"
        label_format: One of 'name', 'id', 'name_and_id'. Default  is "name"
        inc_unlabelled_mrca: Whether to include node labels form synth that do not correspond to taxa
                             Default  is False
        standardize: Whether to standardize taxon labels by removing problem characters. Default is True

    Returns:
        tree, unknown_ids
        tree: a dendropy tree object with taxa labelled acrording to 'label_format'
        unknown_ids: a list of the input ott_ids that were not found

    """
    
    # call synth tree
    curr_ids = copy.deepcopy(ott_ids) #track who we lost
    call_record = OT.ws.tree_of_life_induced_subtree(ott_ids=curr_ids,
                                                     label_format='id')#This needs to be id
    # often some ids are not found - cull but track
    unknown_ids = []
    unknown_dict = {}
    if call_record.response_dict.get('unknown'):
        unknown_ids = call_record.response_dict['unknown'].keys()
        OT._cull_unknown_ids_from_args(call_record, node_ids=None, ott_ids=curr_ids)
        for unk in unknown_ids:
            uid = unk.strip('ott') #URL for taxonomy needs integer
            tax_inf = OT.taxon_info(ott_id=uid).response_dict
            tax_inf['url'] = "https://tree.opentreeoflife.org/taxonomy/browse?id={}".format(uid)
            unknown_dict[unk] = tax_inf

    call_record = OT.ws.tree_of_life_induced_subtree(ott_ids=curr_ids,
                                                     label_format='name_and_id')

    
    assert label_format in ['name', 'id', 'name_and_id'] ##this only apply's to the re-labeled output, not the first call
    relabel, relabel_ott_ids, broken_dict = _gather_broken_taxa_info(call_record.response_dict['broken'], label_format)

    labelled_tree = copy.deepcopy(call_record.tree)
    all_labels = set()
    for taxon in labelled_tree.taxon_namespace:#Are these necessarily tips???
        all_labels.add(taxon.label)
        if taxon.label.startswith('mrca'):
            assert taxon.label in relabel
            for brok_taxon in relabel_ott_ids[taxon.label]:
                broken_dict[brok_taxon]['is_tip'] = True
            taxon.label = 'MRCA of taxa in '+' '.join(relabel[taxon.label])
        else:
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
                added_taxa = ' and MRCA of taxa in '+' '.join(relabel[ott])
                taxon.label = new_label + added_taxa
                for brok_taxon in relabel_ott_ids[ott]:
                    broken_dict[brok_taxon]['is_tip'] = True
            else:
                taxon.label =  new_label

    for node in labelled_tree:
        if node.label and node.label != '':
            if node.taxon:
                node.label = None
            else:
                all_labels.add(node.label)
                if node.label.startswith('mrca'):
                    if node.label in relabel:
                        for brok_taxon in relabel_ott_ids[node.label]:
                            broken_dict[brok_taxon]['is_tip'] = False
                        node.label = 'MRCA of taxa in '+' '.join(relabel[node.label])
                    elif inc_unlabelled_mrca:
                        pass
                    else:
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
                        added_taxa = 'MRCA of taxa in '+' '.join(relabel[ott])
                        node.label = new_label + added_taxa
                        for brok_taxon in relabel_ott_ids[ott]:
                            broken_dict[brok_taxon]['is_tip'] = False
                    else:
                        node.label =  new_label

    if standardize == True:
        labelled_tree = standardize_labels(labelled_tree)

    return {'labelled_tree':labelled_tree,'original_tree':call_record.tree, 'unknown_ids':unknown_dict, 'non-monophyletic_taxa':broken_dict}