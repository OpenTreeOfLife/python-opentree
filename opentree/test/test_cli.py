import unittest
import subprocess
from opentree import OTCommandLineTool

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