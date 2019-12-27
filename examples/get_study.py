#!/usr/bin/env python3
import json

from opentree import OTCommandLineTool, get_suppressed_taxon_flag_expl_url

cli = OTCommandLineTool(usage='Fetch a study by its phylesystem study ID')
cli.parser.add_argument(dest='study_id', help="The ID of the study to retrieve")
OT, args = cli.parse_cli()
output = OT.get_study(args.study_id)

print(json.dumps(output.response_dict, indent=2, sort_keys=True))

