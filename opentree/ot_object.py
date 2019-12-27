#!/usr/bin/env python3

from .ws_wrapper import (OTWebServicesError,
                         WebServiceRunMode,
                         )
from .ot_ws_wrapper import OTWebServiceWrapper


class OpenTree(object):
    """This class is intended to provide a high-level wrapper for interaction with OT web services and data.
    The method names are intended to be clear to a wide variety of users, rather than (necessarily matching
    the API calls directly.

    """

    def __init__(self, api_endpoint='production', run_mode=WebServiceRunMode.RUN):
        self._api_endpoint = api_endpoint
        self._run_mode = run_mode
        self._ws = None

    @property
    def ws(self):
        if self._ws is None:
            self._ws = OTWebServiceWrapper(api_endpoint=self._api_endpoint,
                                           run_mode=self._run_mode)
        return self._ws

    def about(self):
        tax_about = self.ws.taxonomy_about()
        tree_about = self.ws.tree_of_life_about()
        return {'taxonomy_about': tax_about,
                'synth_tree_about': tree_about
                }

    def get_study(self, study_id):
        return self.ws.study(study_id)

    def studies_properties(self):
        return self.ws.studies_properties()

    def find_studies(self, value, search_property, exact=False, verbose=False):
        return self.ws.studies_find_studies(value, search_property=search_property, exact=exact, verbose=verbose)


    def find_trees(self, value, search_property, exact=False, verbose=False):
        return self.ws.studies_find_trees(value, search_property=search_property, exact=exact, verbose=verbose)


    def taxon_info(self, ott_id=None, source_id=None, include_lineage=False,
                   include_children=False, include_terminal_descendants=False):
        return self.ws.taxonomy_taxon_info(ott_id=ott_id, source_id=source_id,
                                           include_lineage=include_lineage,
                                           include_children=include_children,
                                           include_terminal_descendants=include_terminal_descendants)

    def taxon_mrca(self, ott_ids=None, ignore_unknown_ids=True):
        while True:
            call_record = self.ws.taxonomy_mrca(ott_ids=ott_ids)
            if call_record:
                return call_record
            if not ignore_unknown_ids:
                msgtemplate = 'Call to taxonomy/mrca failed with the message "{}"'
                message = call_record.response_dict['message']
                raise OTWebServicesError(msgtemplate.format(message))
            self._cull_unknown_ids_from_args(call_record, [], ott_ids)

    def taxon_subtree(self, ott_id=None, label_format="name_and_id"):
        return self.ws.taxonomy_subtree(ott_id=ott_id, label_format=label_format)

    def tnrs_contexts(self):
        return self.ws.tnrs_contexts()

    def tnrs_infer_context(self, names):
        return self.ws.tnrs_infer_context(names)

    def tnrs_match(self, names, context_name=None, do_approximate_matching=False, include_suppressed=False):
        return self.ws.tnrs_match_names(names, context_name=context_name,
                                        do_approximate_matching=do_approximate_matching,
                                        include_suppressed=include_suppressed)

    def tnrs_autocomplete(self, name, context_name=None, include_suppressed=False):
        return self.ws.tnrs_autocomplete_name(name, context_name=context_name, include_suppressed=include_suppressed)

    def synth_node_info(self, node_ids=None, node_id=None, ott_id=None, include_lineage=False):
        return self.ws.tree_of_life_node_info(node_ids=node_ids, node_id=node_id, ott_id=ott_id,
                                              include_lineage=include_lineage)

    def synth_subtree(self, node_id=None, ott_id=None,
                      tree_format="newick", label_format="name_and_id",
                      height_limit=None):
        return self.ws.tree_of_life_subtree(node_id=node_id, ott_id=ott_id,
                                            tree_format=tree_format,
                                            label_format=label_format,
                                            height_limit=height_limit)

    def synth_induced_tree(self, node_ids=None,
                           ott_ids=None, label_format="name_and_id",
                           ignore_unknown_ids=True):
        while True:
            call_record = self.ws.tree_of_life_induced_subtree(node_ids=node_ids,
                                                               ott_ids=ott_ids,
                                                               label_format=label_format)
            if call_record:
                return call_record
            if not ignore_unknown_ids:
                msgtemplate = 'Call to tree_of_life/induced_subtree failed with the message "{}"'
                message = call_record.response_dict['message']
                raise OTWebServicesError(msgtemplate.format(message))
            self._cull_unknown_ids_from_args(call_record, node_ids, ott_ids)

    def synth_mrca(self, node_ids=None, ott_ids=None, ignore_unknown_ids=True):
        while True:
            call_record = self.ws.tree_of_life_mrca(node_ids=node_ids,
                                                    ott_ids=ott_ids)
            if call_record:
                return call_record
            if not ignore_unknown_ids:
                msgtemplate = 'Call to tree_of_life/mrca failed with the message "{}"'
                message = call_record.response_dict['message']
                raise OTWebServicesError(msgtemplate.format(message))
            self._cull_unknown_ids_from_args(call_record, node_ids, ott_ids)

    # noinspection PyMethodMayBeStatic
    def _cull_unknown_ids_from_args(self, call_record, node_ids, ott_ids):
        unknown_ids = call_record.response_dict['unknown']
        for u in unknown_ids:
            if node_ids and u in node_ids:
                node_ids.remove(u)
            else:
                assert u.startswith('ott')
                ui = int(u[3:])
                if ott_ids and (ui in ott_ids):
                    ott_ids.remove(ui)
