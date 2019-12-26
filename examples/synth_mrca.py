#!/usr/bin/env python3
import json
import sys
from opentree import OTCommandLineTool

cli = OTCommandLineTool(usage='Display node information about the Most Recent Common Ancestor of a sete of IDs')
cli.parser.add_argument('--ott-ids', default=None, type=str,
                        help='a comma separated list of OTT ids')
cli.parser.add_argument('--node-ids', default=None, type=str,
                        help='a comma separated list of node ids')
OT, args = cli.parse_cli()

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
node_id_list = [i.strip().lower() for i in args.node_ids.split(',')]

output = OT.synth_mrca(node_ids=node_id_list, ott_ids=ott_id_list)

print(json.dumps(output.response_dict, indent=2, sort_keys=True))
