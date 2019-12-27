#!/usr/bin/env python3
import json

from opentree import OTCommandLineTool, process_ott_and_node_id_list_args

cli = OTCommandLineTool(usage='Display node information about the Most Recent Common Ancestor of a sete of IDs',
                        common_args=("ott-ids", "node-ids"))
OT, args = cli.parse_cli()
ott_id_list, node_id_list = process_ott_and_node_id_list_args(args)
output = OT.synth_mrca(node_ids=node_id_list, ott_ids=ott_id_list)

print(json.dumps(output.response_dict, indent=2, sort_keys=True))
