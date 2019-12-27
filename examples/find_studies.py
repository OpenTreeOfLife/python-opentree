#!/usr/bin/env python3
import json

from opentree import OTCommandLineTool

cli = OTCommandLineTool(usage='Look up studies in the "phylesystem" set of phylogenetic studies that are in the Open '
                        'system')
cli.parser.add_argument("value", help="The value of the property to match")
cli.parser.add_argument("--property", default=None, required=True,
                        help='The name of the field to search through.')
cli.parser.add_argument("--verbose", action="store_true", help='include meta-data in response')
cli.parser.add_argument("--exact", action="store_true", help='disables fuzzy matching')
OT, args = cli.parse_cli()

output = OT.find_studies(args.value, search_property=args.property, verbose=args.verbose, exact=args.exact)

print(json.dumps(output.response_dict, indent=2, sort_keys=True))
