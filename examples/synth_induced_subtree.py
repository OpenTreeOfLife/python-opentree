#!/usr/bin/env python3
from opentree import OTCommandLineTool, process_ott_id_and_node_id_args

cli = OTCommandLineTool(usage='Display taxonomy and synthetic tree information '
                              'returned by the "about" API calls.',
                        common_args=("ott-ids", "node-ids"))
OT, args = cli.parse_cli()
ott_id_list, node_id_list = process_ott_id_and_node_id_args(args)
output = OT.synth_induced_tree(node_ids=node_id_list, ott_ids=ott_id_list)
print(output.tree.as_ascii_plot())
