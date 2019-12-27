#!/usr/bin/env python3
import json
import sys

from opentree import OTCommandLineTool, process_ott_and_node_id_list_args

cli = OTCommandLineTool(usage='Display taxonomic information about the Most Recent Common Ancestor of a set of IDs',
                        common_args=("ott-ids", ))
OT, args = cli.parse_cli()
ott_id_list = process_ott_and_node_id_list_args(args)[0]
if not ott_id_list:
    sys.exit('--ott-ids must be provided.\n')
output = OT.taxon_mrca(ott_ids=ott_id_list)

print(json.dumps(output.response_dict, indent=2, sort_keys=True))
