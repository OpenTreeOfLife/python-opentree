#!/usr/bin/env python3
import sys
import json
from opentree import OTCommandLineTool


cli = OTCommandLineTool(usage='Display node info for the synthetic tree node(s) requested')
cli.parser.add_argument('--ott-ids', default=None, type=str,
                        help='a comma separated list of OTT ids')
cli.parser.add_argument('--node-ids', default=None, type=str,
                        help='a comma separated list of node ids')
cli.parser.add_argument('--include-lineage', action='store_true',
                        help='Return the lineage of nodes back to the root of the tree')
OT, args = cli.parse_cli()
if args.ott_ids is None and args.node_ids is None:
    sys.exit('Either --node-ids or --ott-ids must be provided.\n')

ott_id = None
node_id_list = []
if args.ott_ids:
    x = [i.strip().lower() for i in args.ott_ids.split(',')]
    ott_id_list = []
    for el in x:
        unaltered_el = el
        if el.startswith('ott'):
            el = el[3:]
        try:
            ott_id_list.append(int(el))
        except:
            sys.exit('Expecting each ott ID to be an integer or a string starting with "ott". '
                     'Found "{}"\n'.format(unaltered_el))
    if len(ott_id_list) != 1:
        node_id_list = ['ott{}'.format(i) for i in ott_id_list]
    else:
        ott_id = ott_id_list[0]

if args.node_ids:
    x = [i.strip().lower() for i in args.ott_ids.node_ids(',')]
    node_id_list.extend(x)

if len(node_id_list) == 1:
    output = OT.synth_node_info(node_id=node_id_list[0], include_lineage=args.include_lineage)
elif len(node_id_list) > 1:
    output = OT.synth_node_info(node_ids=node_id_list, include_lineage=args.include_lineage)
else:
    assert ott_id is not None
    output = OT.synth_node_info(ott_id=ott_id, include_lineage=args.include_lineage)
print(json.dumps(output.response_dict, indent=2, sort_keys=True))
