#!/usr/bin/env python3
import json

from opentree import OTCommandLineTool

cli = OTCommandLineTool(usage='Look up a minimal context name of a set of names')
cli.parser.add_argument("names", nargs="+", help="names to match")
OT, args = cli.parse_cli()

output = OT.tnrs_infer_context(args.names)

print(json.dumps(output.response_dict, indent=2, sort_keys=True))
