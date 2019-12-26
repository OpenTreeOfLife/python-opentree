#!/usr/bin/env python3
import json
import sys
from opentree import OTCommandLineTool

cli = OTCommandLineTool(usage='Display node information about the Most Recent Common Ancestor of a sete of IDs',
                        add_ott_ids_arg=True,
                        add_node_ids_arg=True
                        )
OT, args = cli.parse_cli()
ott_id_list, node_id_list = process_ott_id_and_node_id_args(args)
output = OT.synth_mrca(node_ids=node_id_list, ott_ids=ott_id_list)

print(json.dumps(output.response_dict, indent=2, sort_keys=True))
