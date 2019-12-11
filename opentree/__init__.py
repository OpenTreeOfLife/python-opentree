#!/usr/bin/env python3
__version__ = "0.0.1"  # sync with setup.py

import logging

import dendropy
from .wswrapper import WebServiceWrapperRaw

_LOG = logging.getLogger('opentree')


class OTWebServicesError(Exception):
    pass


class OTClientError(Exception):
    pass



class Converter(object):
    def tree_from_newick(self, newick, suppress_internal_node_taxa=False):
        return dendropy.Tree.get(data=newick, schema="newick", suppress_internal_node_taxa=suppress_internal_node_taxa)


class OTWebServiceWrapper(WebServiceWrapperRaw):
    def __init__(self, api_endpoint):
        WebServiceWrapperRaw.__init__(self, api_endpoint)
        self.to_object_converter = Converter()

    def tree_of_life_induced_subtree(self, node_ids=None, ott_ids=None, label_format="name_and_id"):
        d = {"label_format": label_format.lower().strip()}
        if node_ids or ott_ids:
            if node_ids and ott_ids:
                raise ValueError("Only one of `node_ids` and `ott_ids` can be specified")
            if node_ids:
                d["node_ids"] = [str(i) for i in node_ids]
            else:
                d["ott_ids"] = [int(i) for i in ott_ids]
        resp_dict = self._call_api('tree_of_life/induced_subtree', data=d)
        newick = resp_dict['newick']
        return self.to_object_converter.tree_from_newick(newick, suppress_internal_node_taxa=True)


class OpenTree(object):
    def __init__(self):
        self._api_endpoint = 'production'
        self._ws = None

    @property
    def ws(self):
        if self._ws is None:
            self._ws = OTWebServiceWrapper(self._api_endpoint)
        return self._ws

    def tree_for_ott_ids(self, ott_ids):
        return self.ws.tree_of_life_induced_subtree(ott_ids=ott_ids)


# Default-configured wrapper
OT = OpenTree()
