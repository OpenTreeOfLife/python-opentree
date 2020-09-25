#!/usr/bin/env python3
"""
to run:
python examples/synth_induced_subtree.py --ott-ids 770309,913932 --node-ids mrcaott354607ott374748 --oufile tree.nwk

"""
import sys
import argparse
from opentree import OTCommandLineTool, process_ott_and_node_id_list_args

def main(arg_list, out, list_for_results=None):
    cli = OTCommandLineTool(usage='Display taxonomy and synthetic tree information '
                                  'returned by the "about" API calls.',
                            common_args=("ott-ids", "node-ids"))
    cli.parser.add_argument('--outfile', nargs='?', type=argparse.FileType('w'),
                            default=None)
    OT, args = cli.parse_cli(arg_list)
    ott_id_list, node_id_list = process_ott_and_node_id_list_args(args)
    output = OT.synth_induced_tree(node_ids=node_id_list, ott_ids=ott_id_list)
    if list_for_results is not None:
        list_for_results.append(output)
    if out is not None:
            sp = output.tree.as_ascii_plot()
            out.write('{}\n'.format(sp))
    if args.outfile is not None:
            new = (output.response_dict['newick'])
            args.outfile.write('{}\n'.format(new))
    return 0

if __name__  == '__main__':
    rc = main(sys.argv[1:], sys.stdout)
    sys.exit(rc)
