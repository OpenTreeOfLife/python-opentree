#!/usr/bin/env python3
import sys

from opentree import OTCommandLineTool, process_ott_or_node_id_arg

cli = OTCommandLineTool(usage='Gets a subtree of the taxonomic tree tree rooted at the node requested',
                        common_args=("ott-id", ))
cli.parser.add_argument('--label-format', default='name_and_id',
                        help='"name_and_id", "name", or "id" style of labeling newick nodes')
OT, args = cli.parse_cli()

label_format = args.label_format.strip().lower()
if label_format not in ["name_and_id", "name", "id"]:
    sys.exit("Did not recognize --label-format={}\n".format(label_format))


ott_id = process_ott_or_node_id_arg(args)[0]
if ott_id is None:
    sys.exit('--ott-id must be provided.\n')

output = OT.taxon_subtree(ott_id=ott_id, label_format=label_format)

print(output.tree.as_ascii_plot())

