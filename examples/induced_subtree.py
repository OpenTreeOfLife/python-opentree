#!/usr/bin/env python3

from opentree import OT
ott_id_list = [0, 199350, 705358, 153562, 770309, 122359, 962391, 708325,
               465090, 335593, 733093, 66456, 335589, 66463, 675102, 284917, 937560,]
tree = OT.tree_for_ids(ott_ids=ott_id_list)

print(tree.as_ascii_plot())
