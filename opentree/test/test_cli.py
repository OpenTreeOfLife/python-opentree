import unittest
import subprocess
from opentree.ot_command_line_tool import (OTCommandLineTool,
                                          process_ott_and_node_id_list_args,
                                          process_ott_or_node_id_arg)
import sys

class TestCLI(unittest.TestCase):
    def test_diagnose_solution(self):
        url = 'https://tree.opentreeoflife.org/curator/study/view/ot_1344?tab=trees&tree=Tr105486&node=Tn16531763'
        p = subprocess.run(["./examples/diagnose_solution_for.py",
                            "--ott-id", "1066581"],  
                            stdout=subprocess.PIPE, 
                            input='\n'.encode()) #input keeps it from hanging waiting for a subproblem id

        assert url in p.stdout.decode('utf8'), sys.executable       

    def test_cli_obj(self):
        sys.argv = ["/examples/diagnose_solution_for.py", "--ott-id", "1066581"]
        cli = OTCommandLineTool(usage="test_example",
                                common_args=("ott-id",))
        cli.parse_cli()

    def test_arg_parse_both(self):
        sys.argv = ["/examples/synth_induced_subtree.py", "--ott-ids", "770309,913932", "--node-ids", "mrcaott354607ott374748"]
        cli = OTCommandLineTool(usage='Display taxonomy and synthetic tree information '
                                  'returned by the "about" API calls.',
                            common_args=("ott-ids", "node-ids"))
        OT, args = cli.parse_cli()
        ott_id_list, node_id_list = process_ott_and_node_id_list_args(args)

    def test_arg_parse_or(self):
        sys.argv = ["/examples/synth_induced_subtree.py", "--ott-id", "913932",]
        cli = OTCommandLineTool(usage='Display taxonomy and synthetic tree information '
                                  'returned by the "about" API calls.',
                            common_args=("ott-id", "node-id"))
        OT, args = cli.parse_cli()
        process_ott_or_node_id_arg(args)
