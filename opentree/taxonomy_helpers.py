# From Luna's https://github.com/LunaSare/opentree-ipynb/blob/master/py/get_subtree_for_rank.py
import os
import re
import sys
import gzip
import shutil
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


def get_forwarded_ids(ott_ids, forwards_file):
    """Returns a dictionary with new ott_ids for forwarded ott_ids
    """
    assert isinstance(ott_ids, list)
    resp_dict = {}
    fwd_dict = {}
    fi=open(forwards_file)
    header = fi.readline()
    for lin in fi:
        lii = lin.split()
        fwd_dict[int(lii[0])]=lii[1]
    for ott_id in ott_ids:
        if 'ott' in ott_id:
            ott_id = ott_id.strip('ott')
        resp_dict[ott_id] = fwd_dict.get(int(ott_id))
    return resp_dict

def clean_taxonomy_file(taxonomy_file):
    """Geneartes a pruned taxonomy.
    cleans up the word 'species' and the flag 'no rank - terminal', which is not associated to higher taxonomic ranks
    """
    taxon_dir = os.path.dirname(taxonomy_file)
    output_path = "{}/taxonomy_clean.tsv".format(taxon_dir)
    if not os.path.exists(output_path):
        # clean taxonomy file, writes cleaned file to taxonomy_clean.tsv
        os.system('grep -a -v "major_rank_conflict" ' + taxonomy_file + ' | egrep -a -v "varietas" | egrep -a -v "no rank" | egrep -a -v "Incertae" | egrep -a -v "incertae" | egrep -a -v "uncultured" | egrep -a -v "barren" | egrep -a -v "extinct" | egrep -a -v "unplaced" | egrep -a -v "hidden" | egrep -a -v "inconsistent" | egrep -a -v "synonym" > {}'.format(output_path))
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
    if not os.path.exists(output_path):
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