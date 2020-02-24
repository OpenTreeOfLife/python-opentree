#!/usr/bin/env python3
import json
import sys
from opentree import OTCommandLineTool

def main(arg_list, out, list_for_results=None):
    cli = OTCommandLineTool(usage='Look up a minimal context name of a set of names')
    cli.parser.add_argument("names", nargs="+", help="names to match")
    OT, args = cli.parse_cli(arg_list)

    output = OT.tnrs_infer_context(args.names)
    if list_for_results is not None:
        list_for_results.append(output)
    if out is not None:
        sf = json.dumps(output.response_dict, indent=2, sort_keys=True)
        out.write('{}\n'.format(sf))
    return 0

if __name__  == '__main__':
    rc = main(sys.argv, sys.stdout)
    sys.exit(rc)
