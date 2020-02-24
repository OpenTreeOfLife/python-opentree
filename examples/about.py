#!/usr/bin/env python3

import sys
from opentree import OTCommandLineTool

def main(arg_list, out, list_for_results=None):
    cli = OTCommandLineTool(usage='Display taxonomy and synthetic tree information '
                              'returned by the "about" API calls.')
    OT = cli.parse_cli(arg_list)[0]
    about = OT.about()
    if list_for_results is not None:
        list_for_results.append(about)
    if out is None:
        return 0
    for k in about.keys():
        call_record = about[k]
        if call_record:
            print(k)
            call_record.write_response(out)
            print('')
    return 0

if __name__  == '__main__':
    rc = main(sys.argv, sys.stdout)
    sys.exit(rc)
