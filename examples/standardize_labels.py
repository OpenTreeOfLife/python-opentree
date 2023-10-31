#!/usr/bin/env python3

import argparse
import dendropy
from opentree import taxonomy_helpers


parser = argparse.ArgumentParser()
parser.add_argument("-i","--input", help="Input tree")
parser.add_argument("-o","--output", help="Output filename.")
parser.add_argument("-c","--characters", help="characters to strip.", nargs="?", default="():#")
parser.add_argument("-r","--replace", help="character to insert", nargs="?", default="_")



args = parser.parse_args()

tree = dendropy.Tree.get(path=args.input, schema='newick')

taxonomy_helpers.standardize_labels(tree, prob_char=args.characters, replace_w = args.replace)

tree.write(path=args.output, schema="newick")