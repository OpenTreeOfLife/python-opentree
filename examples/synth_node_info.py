#!/usr/bin/env python3
import sys
import json
from opentree import (OTCommandLineTool, process_ott_and_node_id_list_args)

def main(arg_list, out, list_for_results=None):
    cli = OTCommandLineTool(usage='Display node info for the synthetic tree node(s) requested',
                            common_args=("ott-ids", "node-ids"))
    cli.parser.add_argument('--include-lineage', action='store_true',
                            help='Return the lineage of nodes back to the root of the tree')
    OT, args = cli.parse_cli(arg_list)
    ott_id_list, node_id_list = process_ott_and_node_id_list_args(args)
    # use node_id_list if there are multiple. This is an odd call in the API
    if (not node_id_list) and (not ott_id_list):
        raise ValueError('Either --node-ids or --ott-ids must be provided.\n')
    if len(ott_id_list) > 1 or (node_id_list and ott_id_list):
        node_id_list.extend(['ott{}'.format(i) for i in ott_id_list])
        ott_id_list.clear()
    if len(node_id_list) == 1:
        output = OT.synth_node_info(node_id=node_id_list[0], include_lineage=args.include_lineage)
    elif len(node_id_list) > 1:
        output = OT.synth_node_info(node_ids=node_id_list, include_lineage=args.include_lineage)
    else:
        assert len(ott_id_list) == 1
        ott_id = ott_id_list[0]
        assert ott_id is not None
        output = OT.synth_node_info(ott_id=ott_id, include_lineage=args.include_lineage)

    if list_for_results is not None:
        list_for_results.append(output)
    if out is not None:
        sp = json.dumps(output.response_dict, indent=2, sort_keys=True)
        out.write('{}\n'.format(sp))
    return 0


if __name__  == '__main__':
    rc = main(sys.argv[1:], sys.stdout)
    sys.exit(rc)
