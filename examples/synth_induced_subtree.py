#!/usr/bin/env python3
import sys
from opentree import OTCommandLineTool

cli = OTCommandLineTool(usage='Display taxonomy and synthetic tree information '
                              'returned by the "about" API calls.')
cli.parser.add_argument('--ott-ids', default=None, type=str,
                        help='a comma separated list of OTT ids')
OT, args = cli.parse_cli()
if args.ott_ids is None:
    ott_id_list = [0, 199350, 705358, 153562, 770309, 122359, 962391, 708325,
                   465090, 335593, 733093, 66456, 335589, 66463, 675102, 284917, 937560, ]
else:
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

output = OT.induced_synth_tree(ott_ids=ott_id_list)

print(output.tree.as_ascii_plot())
