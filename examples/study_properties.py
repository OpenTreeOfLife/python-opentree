#!/usr/bin/env python3

import json
from opentree import OTCommandLineTool

cli = OTCommandLineTool(usage='Displays the searchable properties for studies and trees in the "phylesystem"')
OT = cli.parse_cli()[0]
output = OT.studies_properties()
print(json.dumps(output.response_dict, indent=2, sort_keys=True))
