#!/usr/bin/env python3

from .object_conversion import get_object_converter
from .ws_wrapper import (WebServiceRunMode,
                         WebServiceWrapper,
                         )


class OTWebServiceWrapper(WebServiceWrapper):
    """This class provides a wrapper to the Open Tree of Life web service methods.
    Actual HTTP calls are handled by methods implemented in the base class for clarity of this code.
    API method calls will be mappable to methods in this class. The methods implemented here do argument checking
    and conversion of the returned JSON to more usable objects.
    """

    def __init__(self, api_endpoint, run_mode=WebServiceRunMode.RUN):
        WebServiceWrapper.__init__(self, api_endpoint, run_mode=run_mode)
        self.to_object_converter = get_object_converter('dendropy')

    def tree_of_life_induced_subtree(self, node_ids=None, ott_ids=None, label_format="name_and_id"):
        d = {"label_format": label_format.lower().strip()}
        if not (node_ids or ott_ids):
            raise ValueError("Either node_ids or ott_ids must be provided")
        if node_ids:
            d["node_ids"] = [str(i) for i in node_ids]
        if ott_ids:
            d["ott_ids"] = [int(i) for i in ott_ids]
        return self._call_api('tree_of_life/induced_subtree', data=d, demand_success=False)

    def taxonomy_about(self):
        return self._call_api('taxonomy/about')

    def tree_of_life_about(self):
        return self._call_api('tree_of_life/about')
