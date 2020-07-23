#!/usr/bin/env python3

import json
import sys
from opentree import OTCommandLineTool

def main(arg_list, out, list_for_results=None):
    cli = OTCommandLineTool(usage='Displays the searchable properties for studies and trees in the "phylesystem"')
    OT = cli.parse_cli(arg_list)[0]
    output = OT.studies_properties()
    if list_for_results is not None:
        list_for_results.append(output)
    if out is not None:
        sf = json.dumps(output.response_dict, indent=2, sort_keys=True)
        out.write('{}\n'.format(sf))
    return 0

if __name__  == '__main__':
    rc = main(sys.argv[1:], sys.stdout)
    sys.exit(rc)
