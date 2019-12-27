#!/usr/bin/env python3

import json

from opentree import OTCommandLineTool

cli = OTCommandLineTool(usage='Display the Open Tree TNRS named contexts')
OT = cli.parse_cli()[0]

output = OT.tnrs_contexts()

print(json.dumps(output.response_dict, indent=2, sort_keys=True))
