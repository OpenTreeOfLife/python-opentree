#!/usr/bin/env python3

import json
import sys
from opentree import OTCommandLineTool, process_ott_and_node_id_list_args

def main(arg_list, out, list_for_results=None):
    cli = OTCommandLineTool(usage='Display node information about the Most Recent Common Ancestor of a set of IDs',
                            common_args=("ott-ids", "node-ids"))
    OT, args = cli.parse_cli(arg_list)
    ott_id_list, node_id_list = process_ott_and_node_id_list_args(args)
    output = OT.synth_mrca(node_ids=node_id_list, ott_ids=ott_id_list)
    if list_for_results is not None:
        list_for_results.append(output)
    if out is not None:
        sp = json.dumps(output.response_dict, indent=2, sort_keys=True)
        out.write('{}\n'.format(sp))
    return 0

if __name__  == '__main__':
    rc = main(sys.argv[1:], sys.stdout)
    sys.exit(rc)
