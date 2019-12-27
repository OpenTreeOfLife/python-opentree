#!/usr/bin/env python3
import sys

from opentree import OTCommandLineTool, process_ott_or_node_id_arg

cli = OTCommandLineTool(usage='Gets a subtree of the synthetic tree rooted at the node requested',
                        common_args=("ott-id", "node-id"))
cli.parser.add_argument('--format', default='newick',
                        help='"newick" or "arguson" tree format')
cli.parser.add_argument('--label-format', default='name_and_id',
                        help='"name_and_id", "name", or "id" style of labeling newick nodes')
cli.parser.add_argument('--height-limit', default=None, type=int,
                        help='number of levels to return. -1 for unlimited (newick only)')
OT, args = cli.parse_cli()

tree_format = args.format.strip().lower()
if tree_format not in ["newick", "arguson"]:
    sys.exit("Did not recognize --format={}\n".format(tree_format))
if args.height_limit is None:
    if tree_format == "newick":
        height_limit = -1
    else:
        height_limit = 3
else:
    height_limit = args.height_limit
    if height_limit < -1:
        sys.exit('Expecting height limit to be >= -1.')
label_format = args.label_format.strip().lower()
if label_format not in ["name_and_id", "name", "id"]:
    sys.exit("Did not recognize --label-format={}\n".format(label_format))


ott_id, node_id = process_ott_or_node_id_arg(args)
# use node_id_list if there are multiple. This is an odd call in the API
if (ott_id is None) and (node_id is None):
    sys.exit('Either --node-ids or --ott-ids must be provided.\n')

if ott_id is not None:
    output = OT.synth_subtree(ott_id=ott_id, tree_format=tree_format, label_format=label_format,
                              height_limit=height_limit)
else:
    output = OT.synth_subtree(node_id=node_id, tree_format=tree_format, label_format=label_format,
                              height_limit=height_limit)

print(output.tree.as_ascii_plot())

