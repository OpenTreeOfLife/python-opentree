#!/usr/bin/env python3
import json

from opentree import OTCommandLineTool

cli = OTCommandLineTool(usage='Fetch a tree by its phylesystem study ID and tree ID')
cli.parser.add_argument(dest='study_id', help="The ID of the study to retrieve")
cli.parser.add_argument(dest='tree_id', help="The ID of the study to retrieve")
OT, args = cli.parse_cli()
output = OT.get_tree(args.study_id, args.tree_id)

print(json.dumps(output.response_dict, indent=2, sort_keys=True))

