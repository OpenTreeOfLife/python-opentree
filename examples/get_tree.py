#!/usr/bin/env python3
import json
import sys

from opentree import OTCommandLineTool

def main(arg_list, out, list_for_results=None):
    cli = OTCommandLineTool(usage='Fetch a tree by its phylesystem study ID and tree ID')
    cli.parser.add_argument(dest='study_id', help="The ID of the study to retrieve")
    cli.parser.add_argument(dest='tree_id', help="The ID of the study to retrieve")
    cli.parser.add_argument('--format', default='nexson', type=str,
                            help='one of: "newick", "nexson", "nexus", or "object"]')
    OT, args = cli.parse_cli(arg_list)
    output = OT.get_tree(args.study_id, args.tree_id, tree_format=args.format)
    if list_for_results is not None:
        list_for_results.append(output)
    if out is None:
        return 0
    if args.format == 'nexson':
        out.write('{}\n'.format(json.dumps(output.response_dict, indent=2, sort_keys=True)))
    else:
        out.write('{}\n'.format(output.tree))
    return 0

if __name__  == '__main__':
    rc = main(sys.argv[1:], sys.stdout)
    sys.exit(rc)