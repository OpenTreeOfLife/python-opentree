#!/usr/bin/env python3

from opentree import OT


about = OT.about()

for k in about.keys():
    print('{}:\n{}\n'.format(k, about[k]))