#!/usr/bin/env python3
import sys
import json
from opentree import OTCommandLineTool


cli = OTCommandLineTool(usage='Display taxonomic info (based on the Open Tree Taxonomy) for a taxon ID',
                        common_args=("ott-id", ))
cli.parser.add_argument('--source-id', default=None, type=str,
                        help='A source taxonomy id for the taxon of interest, in the form prefix:id, for'
                             ' example ncbi:9443, irmng:11338. '
                             'Valid prefixes are currently ncbi, gbif, worms, if, and irmng. '
                             'Either ott_id or source_id must be given, but not both')
cli.parser.add_argument('--include-lineage', action='store_true',
                        help='Return the lineage of nodes back to the root of the tree')
cli.parser.add_argument('--include-children', action='store_true',
                        help='Return information about all the children of this taxon')
cli.parser.add_argument('--include-terminal-descendants', action='store_true',
                        help='Return a list of terminal OTT IDs that are descendants of this taxon')
OT, args = cli.parse_cli()

kwargs = {'include_children': args.include_children,
          'include_lineage': args.include_lineage,
          'include_terminal_descendants': args.include_terminal_descendants,
          }
if args.ott_id:
    o = args.ott_id if not args.ott_id.startswith('ott') else args.ott_id[3:]
    try:
        ott_id = int(o)
    except:
        sys.exit('Expecting each ott ID to be an integer or a string starting with "ott". '
                 'Found "{}"\n'.format(args.ott_id))
    else:
        output = OT.taxon_info(ott_id=ott_id, **kwargs)
elif args.source_id:
    if ':' not in args.source_id:
        sys.exit('Expecting a source ID to be in prefix:ID form. '
                 'Found "{}"\n'.format(args.source_id))
    output = OT.taxon_info(source_id=args.source_id, **kwargs)
else:
    sys.exit('Expecting either --ott-id or --source-id to be provided\n')
print(json.dumps(output.response_dict, indent=2, sort_keys=True))
