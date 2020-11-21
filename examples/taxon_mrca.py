#!/usr/bin/env python3
import json
import sys

from opentree import OTCommandLineTool, process_ott_and_node_id_list_args

def main(arg_list, out, list_for_results=None):
    cli = OTCommandLineTool(usage='Display taxonomic information about the Most Recent Common Ancestor of a set of IDs',
                            common_args=("ott-ids", ))
    OT, args = cli.parse_cli(arg_list)
    ott_id_list = process_ott_and_node_id_list_args(args)[0]
    if not ott_id_list:
        sys.exit('--ott-ids must be provided.\n')
    output = OT.taxon_mrca(ott_ids=ott_id_list)
    if list_for_results is not None:
        list_for_results.append(output)
    if out is not None:
        sf = json.dumps(output.response_dict, indent=2, sort_keys=True)
        out.write('{}\n'.format(sf))
    return 0

if __name__  == '__main__':
    try:
        rc = main(sys.argv[1:], sys.stdout)
    except Exception as x:
        sys.exit('{}\n'.format(str(x)))
    else:
        sys.exit(rc)
