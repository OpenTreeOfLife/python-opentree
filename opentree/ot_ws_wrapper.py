#!/usr/bin/env python3
# Class for direct mapping between Open Tree API -> python object

from .object_conversion import get_object_converter
from .ws_wrapper import (WebServiceRunMode,
                         WebServiceWrapper,
                         )
from datetime import datetime

class OTWebServiceWrapper(WebServiceWrapper):
    """This class provides a wrapper to the Open Tree of Life web service methods.
    Actual HTTP calls are handled by methods implemented in the base class for clarity of this code.
    API method calls will be mappable to methods in this class. The methods implemented here do argument checking
    and conversion of the returned JSON to more usable objects.
    """

    def __init__(self, api_endpoint, run_mode=WebServiceRunMode.RUN):
        WebServiceWrapper.__init__(self, api_endpoint, run_mode=run_mode)
        self.to_object_converter = get_object_converter('dendropy')

    def _one_and_only_one(self, api_method, param_dict):
        num = sum([1 if bool(v) else 0 for v in param_dict.values()])
        if num == 1:
            for k, v in param_dict.items():
                if v:
                    return k, v
        sl = list(param_dict.keys())
        sl.sort()
        c = '", "'.join(sl)
        raise ValueError('Exactly 1 of "{}" must be provided for a call to {}'.format(c, api_method))

    def tree_of_life_induced_subtree(self, node_ids=None, ott_ids=None, label_format="name_and_id"):
        d = {"label_format": label_format.lower().strip()}
        if not (node_ids or ott_ids):
            raise ValueError("Either node_ids or ott_ids must be provided")
        if node_ids:
            d["node_ids"] = [str(i) for i in node_ids]
        if ott_ids:
            d["ott_ids"] = [int(i) for i in ott_ids]
        return self._call_api('tree_of_life/induced_subtree', data=d, demand_success=False)

    def tree_of_life_mrca(self, node_ids=None, ott_ids=None, ):
        d = {}
        if not (node_ids or ott_ids):
            raise ValueError("Either node_ids or ott_ids must be provided")
        if node_ids:
            d["node_ids"] = [str(i) for i in node_ids]
        if ott_ids:
            d["ott_ids"] = [int(i) for i in ott_ids]
        return self._call_api('tree_of_life/mrca', data=d, demand_success=False)

    def tree_of_life_node_info(self, node_ids=None, node_id=None, ott_id=None, include_lineage=False):
        d = {"include_lineage": bool(include_lineage)}
        cdict = {"node_ids": node_ids, "node_id":node_id, "ott_id": ott_id}
        name, value = self._one_and_only_one('tree_of_life/node_info', cdict)
        if name == "node_ids":
            d["node_ids"] = [str(i) for i in value]
        elif name == "ott_id":
            d["ott_id"] = int(value)
        else:
            assert name == "node_id"
            d["node_id"] = str(value)
        return self._call_api('tree_of_life/node_info', data=d, demand_success=True)

    def taxonomy_about(self):
        return self._call_api('taxonomy/about')


    def tree_of_life_about(self):
        return self._call_api('tree_of_life/about')

def ot_datetime_str_to_object(xdatestr):
    return datetime.strptime(xdatestr, '%Y-%m-%d %H:%M:%S')

