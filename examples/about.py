#!/usr/bin/env python3
"""Get information on current taxonomy and synthesis tree"""

import sys
import json
from opentree import OTCommandLineTool

def main(arg_list, out, list_for_results=None):
    cli = OTCommandLineTool(usage='Display taxonomy and synthetic tree information '
                              'returned by the "about" API calls.')
    OT = cli.parse_cli()[0]
    about = OT.about()
    if list_for_results is not None:
        list_for_results.append(about)
    if out is None:
        return 0
    for k in about.keys():
        call_record = about[k]
        if call_record:
            print(k)
            sf = json.dumps(call_record, sort_keys=True, indent=2, separators=(',', ': '), ensure_ascii=True)
            print(sf)
            print('')
    return 0

if __name__  == '__main__':
    rc = main(sys.argv, sys.stdout)
    sys.exit(rc)
