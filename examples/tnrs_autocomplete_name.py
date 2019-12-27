#!/usr/bin/env python3
import json

from opentree import OTCommandLineTool, get_suppressed_taxon_flag_expl_url

cli = OTCommandLineTool(usage='Return some names that start with the provided name.')
cli.parser.add_argument("name", help="name string to complete")
cli.parser.add_argument("--context-name", default=None,
                        help='If you know the named Open Tree name searching index, you can supply it here ' 
                             'to limit your search to only a subset of the taxonomny.')
cli.parser.add_argument("--include-suppressed", action="store_true",
                        help='Return taxa that are normally suppressed from TNRS '
                             'results. See {}'.format(get_suppressed_taxon_flag_expl_url()))
OT, args = cli.parse_cli()

output = OT.tnrs_autocomplete(args.name,
                              context_name=args.context_name,
                              include_suppressed=args.include_suppressed)

print(json.dumps(output.response_dict, indent=2, sort_keys=True))

