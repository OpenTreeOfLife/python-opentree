#!/usr/bin/env python3
import json
import sys

from opentree import OTCommandLineTool

def main(arg_list, out, list_for_results=None):
    cli = OTCommandLineTool(usage='Look up studies in the "phylesystem" set of phylogenetic studies that are in the Open '
                        'system')
    cli.parser.add_argument("value", help="The value of the property to match")
    cli.parser.add_argument("--property", default=None, required=True,
                        help='The name of the field to search through.')
    cli.parser.add_argument("--verbose", action="store_true", help='include meta-data in response')
    cli.parser.add_argument("--exact", action="store_true", help='disables fuzzy matching')
    OT, args = cli.parse_cli(arg_list)

    output = OT.find_studies(args.value, search_property=args.property, verbose=args.verbose, exact=args.exact)

    if list_for_results is not None:
        list_for_results.append(output)
    if out is not None:
        sf = json.dumps(output.response_dict, indent=2, sort_keys=True)
        out.write('{}\n'.format(sf))
    return 0

if __name__  == '__main__':
    rc = main(sys.argv[1:], sys.stdout)
    sys.exit(rc)