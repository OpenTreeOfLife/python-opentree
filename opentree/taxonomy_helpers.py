# From Luna's https://github.com/LunaSare/opentree-ipynb/blob/master/py/get_subtree_for_rank.py
import os
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

# the function cleans up the word 'species' and the flag 'no rank - terminal', which is not associated to higher taxonomic ranks
def clean_taxonomy_file(taxonomy_file):
    sys.stdout.write('Cleaning {} file... '.format(taxonomy_file))
    # clean taxonomy file, writes cleaned file to taxonomy_clean.tsv
    os.system('grep -a -v "major_rank_conflict" ' + taxonomy_file + ' | egrep -a -v "varietas" | egrep -a -v "no rank" | egrep -a -v "Incertae" | egrep -a -v "incertae" | egrep -a -v "uncultured" | egrep -a -v "barren" | egrep -a -v "extinct" | egrep -a -v "unplaced" | egrep -a -v "hidden" | egrep -a -v "inconsistent" | egrep -a -v "synonym" > taxonomy_clean.tsv')
    sys.stdout.write("Done.\n")
    return 'taxonomy_clean.tsv'

#def get_families(taxonomy_file):
#    assert os.path.exists(taxonomy_file)
#    for lin in open(taxonomy_file):
#        lii=lin.split('\t')
#        if lii[2].endswith()

def get_ott_ids_for_rank(rank, taxonomy_file):
    assert os.path.exists(taxonomy_file)
    sys.stdout.write("Gathering ott ids from {}\n".format(taxonomy_file))
    all_ranks = ['species', 'genus', 'family', 'order', "class"]
    # clean taxonomy file
    os.system('grep -a "' + rank + '" ' + taxonomy_file + ' | egrep -v "Incertae" | egrep -v "no rank" | egrep -v "major_rank_conflict" | egrep -v "uncultured" | egrep -v "barren" | egrep -v "extinct" | egrep -v "incertae" | egrep -v "unplaced" | egrep -v "hidden" | egrep -v "inconsistent"  | egrep -v "synonym" | egrep -v "in ' + rank + '" | egrep -v "species" | egrep -v "genus" | egrep -v "super' + rank + '" | egrep -v "sub' + rank + '" > taxonomy_red.tsv')
    # extract ott ids from taxonomy reduced file
    taxonomy_tsv = 'taxonomy_red.tsv'
    fi = open(taxonomy_tsv).readlines()
    ott_ids = []
    for lin in fi:
        lii = lin.split('\t')
        ott_ids.append(lii[0])
    ott_ids = list(ott_ids)
    return ott_ids


def get_ott_ids_for_group(group_ott_id, write_file = 'children_ott_ids.txt'):
    sys.stdout.write('Gathering ott ids from group with ott id {}...\n'.format(group_ott_id[0]))
    debug(group_ott_id)
    subtree = OT.taxon_subtree(ott_id = group_ott_id, label_format='name_and_id')
    newick = str(subtree)
    # get ott ids from newick
    ott_ids0 = re.findall(r'ott\d+', newick)
    ott_ids = []
    for item in ott_ids0:
        ott_ids.append(re.findall(r'\d+', item))
    ott_ids = [item for sublist in ott_ids for item in sublist] # flattens the list
    if isinstance(write_file, str):
        with open(write_file, 'w') as f:
            for item in ott_ids:
                print >> f, item
    return ott_ids



def get_ott_ids_X(group_ott_id = None, group_ott_ids_file = None, rank = "family", taxonomy_file = 'ott3.1/taxonomy.tsv', clean = True):
    taxonomy_tsv = taxonomy_file
    # clean taxonomy file
    if clean:
        clean_taxonomy_file(taxonomy_file)
        taxonomy_tsv = 'taxonomy_clean.tsv'
    # extract ott ids from taxonomy reduced file
    if isinstance(group_ott_ids_file, str):
        sys.stdout.write('Getting ott ids from file {}...\n'.format(group_ott_ids_file))
        children_ott_ids = [line.rstrip('\n') for line in open(group_ott_ids_file)]
    else:
        children_ott_ids = get_ott_ids_for_group(group_ott_id)
    sys.stdout.write('Gathering ott ids from {} in group...\n'.format(rank))
    fi = open(taxonomy_tsv).readlines()
    ott_ids = []
    # debug(len(children_ott_ids))
    for line in fi:
        lii = re.split('\t*\|\t*', line)
        if re.match('[0-9]', lii[0]): # skips the headers and other weird lines
            if len(lii) > 2:
                if lii[0] in children_ott_ids:
                    # debug(lii[3])
                    # if re.match(rank, lii[3]):
                    if lii[3] in rank:
                        ott_ids.append(lii[0])
    ott_ids = list(ott_ids)
    return ott_ids

def get_ott_ids_group_and_rank(group_ott_id = None, group_ott_ids_file = None, rank = None, rank_ott_ids_file = None, taxonomy_file = 'ott3.1/taxonomy.tsv', clean = True):
    # clean taxonomy file
    taxonomy_tsv = taxonomy_file
    if clean:
        clean_taxonomy_file(taxonomy_file)
        taxonomy_tsv = 'taxonomy_clean.tsv'
    # get group ott ids
    if isinstance(group_ott_ids_file, str):
        sys.stdout.write('Getting ott ids from file {}...\n'.format(group_ott_ids_file))
        children_ott_ids = [line.rstrip('\n') for line in open(group_ott_ids_file)]
    else:
        children_ott_ids = get_ott_ids_for_group(group_ott_id)
    # get rank ott ids
    rank_ott_ids = get_ott_ids_for_rank(rank, taxonomy_tsv, clean)
    # get rank ott ids that are in children ott ids:
    ott_ids = []
    for item in children_ott_ids:
        if item in rank_ott_ids:
            ott_ids.append(item)