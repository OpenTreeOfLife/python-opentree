#!/usr/bin/env python3

import sys
from opentree import OTCommandLineTool

cli = OTCommandLineTool(usage='Display taxonomy and synthetic tree information '
                              'returned by the "about" API calls.')
OT = cli.parse_cli()[0]
about = OT.about()
for k in about.keys():
    call_record = about[k]
    if call_record:
        print(k)
        call_record.write_response(sys.stdout)
        print('')
