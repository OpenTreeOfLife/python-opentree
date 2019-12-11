#!/usr/bin/env python3
__version__ = "0.0.1"  # sync with setup.py

import logging
from .wswrapper import WebServiceWrapperRaw
from .object_conversion import get_object_converter

_LOG = logging.getLogger('opentree')


class OTWebServiceWrapper(WebServiceWrapperRaw):
    """This class provides a wrapper to the Open Tree of Life web service methods.
    Actual HTTP calls are handled by methods implemented in the base class for clarity of this code.
    API method calls will be mappable to methods in this class. The methods implemented here do argument checking
    and conversion of the returned JSON to more usable objects.
    """
    def __init__(self, api_endpoint):
        WebServiceWrapperRaw.__init__(self, api_endpoint)
        self.to_object_converter = get_object_converter('dendropy')

    def tree_of_life_induced_subtree(self, node_ids=None, ott_ids=None, label_format="name_and_id"):
        d = {"label_format": label_format.lower().strip()}
        if not (node_ids or ott_ids):
            raise ValueError("Either node_ids or ott_ids must be provided")
        if node_ids:
            d["node_ids"] = [str(i) for i in node_ids]
        if ott_ids:
            d["ott_ids"] = [int(i) for i in ott_ids]
        resp_dict = self._call_api('tree_of_life/induced_subtree', data=d)
        newick = resp_dict['newick']
        return self.to_object_converter.tree_from_newick(newick, suppress_internal_node_taxa=True)


class OpenTree(object):
    """This class is intended to provide a high-level wrapper for interaction with OT web services and data.
    The method names are intended to be clear to a wide variety of users, rather than (necessarily matching
    the API calls directly.

    """
    def __init__(self):
        self._api_endpoint = 'production'
        self._ws = None

    @property
    def ws(self):
        if self._ws is None:
            self._ws = OTWebServiceWrapper(self._api_endpoint)
        return self._ws

    def tree_for_ids(self, node_ids=None, ott_ids=None, label_format="name_and_id"):
        return self.ws.tree_of_life_induced_subtree(node_ids=node_ids, ott_ids=ott_ids, label_format=label_format)


# Default-configured wrapper
OT = OpenTree()
