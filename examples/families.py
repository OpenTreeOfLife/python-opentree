#!/usr/bin/env python
# coding: utf-8


from opentree import OT
import json
import os


logfi = open("fam_search.log", 'w')

taxonomy_file = "../ott3.2/taxonomy.tsv"
assert os.path.exists(taxonomy_file)


fam_dict = {}
for lin in open(taxonomy_file):
        lii=lin.split('\t|\t')
        if len(lii[2].split(' ')) > 1:
            pass
        elif lii[2].endswith("aceae"):
            fam_dict[lii[2]]=lii
        elif lii[2].endswith("idae"):
            fam_dict[lii[2]]=lii

json.dump(fam_dict, open("fam_dict.json","w"))
logfi.write("Fam_dict_len {}".format(len(fam_dict)))

maybe_fams = set()
for fam in fam_dict:
    if fam_dict[fam][3] == 'family':
        pass
    else:
        maybe_fams.add(fam)

logfi.write("Maybe_fams_len {}".format(len(maybe_fams_dict)))

fams_in_tree = {}
rev_node_ids = {}
missing_fam = set()
for fam in fam_dict:
    ott_id = fam_dict[fam][0]
    output = OT.synth_node_info(ott_id=ott_id)
    if output.status_code == 200:
        resp = OT.synth_node_info(ott_id=ott_id).response_dict
        fams_in_tree[fam] = resp
        node_id = resp['node_id']
        if node_id not in rev_node_ids:
            rev_node_ids[node_id] = set()
        rev_node_ids[node_id].add(fam)
    else:
        missing_fam.add(fam)


json.dump(rev_node_ids, open("rev_node_ids.json","w"))


lost_fam = missing_fam|maybe_fams
lost_fam = list(lost_fam)


lfout = open("Missing.txt","w")
for fam in lost_fam:
    lfout.write(fam)

lfout.close

node_ids = list(rev_node_ids.keys())
output = OT.synth_induced_tree(node_ids=node_ids)


json.dump(output.response_dict, open("synth_dump.json","w"))

