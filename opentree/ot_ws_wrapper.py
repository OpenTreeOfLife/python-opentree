#!/usr/bin/env python3
# Class for direct mapping between Open Tree API -> python object

from .object_conversion import get_object_converter
from .ws_wrapper import (WebServiceRunMode,
                         WebServiceWrapper,
                         )
from datetime import datetime
import urllib.parse


# noinspection PyMethodMayBeStatic
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

    def studies_properties(self):
        return self._call_api('studies/properties')

    def study(self, study_id, demand_success=False):
        url = 'study/{}'.format(urllib.parse.quote(study_id))
        data = {'output_nexml2json': '1.2.1'}
        return self._call_api(url, http_method='GET', data=data, demand_success=demand_success)

    def tree(self, study_id, tree_id, tree_format="", label_format="ot:originallabel", demand_success=False):
        ext_dict = {'nexus': '.nex', 'newick': '.tre', 'nexson': ''}
        url = 'study/{}/tree/{}{}/?tip_label={}'.format(urllib.parse.quote(study_id), urllib.parse.quote(tree_id),
                                                        ext_dict[tree_format], label_format)
        return self._call_api(url, http_method='GET', demand_success=demand_success)

    def otus(self, study_id, demand_success=False):
        url = 'study/{}/otus'.format(urllib.parse.quote(study_id))
        return self._call_api(url, http_method='GET', demand_success=demand_success)

    # TODO for Luna :) done!
    def conflict(self, study_id, tree_id, compare_to="synth", demand_success=False):
        url = 'conflict/conflict-status?tree1={}%23{}&tree2={}'.format(urllib.parse.quote(study_id),
                                                                       urllib.parse.quote(tree_id), compare_to)
        return self._call_api(url, http_method='GET', demand_success=demand_success)

    def conflict_from_newick(self, input_newick, compare_to, demand_success=False):
        assert(compare_to in ['synth', 'ott'])
        d = {"tree1newick": input_newick,
             "tree2": compare_to }
        return self._call_api('conflict/conflict-status', data=d, demand_success=demand_success)

    def studies_find_studies(self, value, search_property, exact=False, verbose=False):
        d = {"property": str(search_property), "value": str(value), "exact": bool(exact), "verbose": bool(verbose)}
        return self._call_api('studies/find_studies', data=d, demand_success=False)

    def studies_find_trees(self, value, search_property, exact=False, verbose=False):
        d = {"property": str(search_property), "value": str(value), "exact": bool(exact), "verbose": bool(verbose)}
        return self._call_api('studies/find_trees', data=d, demand_success=False)

    def taxonomy_about(self):
        return self._call_api('taxonomy/about')

    def taxonomy_mrca(self, ott_ids):
        if not ott_ids:
            raise ValueError("ott_ids must be provided to a taxonomy/mrca call")
        d = {"ott_ids": [int(i) for i in ott_ids]}
        return self._call_api('taxonomy/mrca', data=d, demand_success=False)

    def taxonomy_taxon_info(self, ott_id=None, source_id=None, include_lineage=False,
                            include_children=False, include_terminal_descendants=False):
        if isinstance(ott_id, str):
            ott_id=ott_id.strip('ott')
            ott_id = int(ott_id)
        cdict = {"source_id": source_id, "ott_id": ott_id}
        id_spec, id_arg = self._one_and_only_one("taxonomy/taxon_info", cdict)
        d = {id_spec: id_arg,
             "include_lineage": include_lineage,
             "include_children": include_children,
             "include_terminal_descendants": include_terminal_descendants, }
        return self._call_api('taxonomy/taxon_info', data=d, demand_success=False)

    def taxonomy_subtree(self, ott_id, label_format=None):
        d = {"ott_id": int(ott_id)}
        if label_format:
            d["label_format"] = str(label_format)
        return self._call_api('taxonomy/subtree', data=d, demand_success=False)

    def tnrs_autocomplete_name(self, name, context_name=None, include_suppressed=False):
        d = {"name": str(name), "include_suppressed": bool(include_suppressed), }
        if context_name is not None:
            d['context_name'] = str(context_name)
        return self._call_api('tnrs/autocomplete_name', data=d, demand_success=False)

    def tnrs_contexts(self):
        return self._call_api('tnrs/contexts', data=None, demand_success=False)

    def tnrs_infer_context(self, names):
        d = {"names": [str(i) for i in names]}
        return self._call_api('tnrs/infer_context', data=d, demand_success=False)

    def tnrs_match_names(self, names, context_name=None, do_approximate_matching=False, include_suppressed=False):
        d = {"names": [str(i) for i in names],
             "do_approximate_matching": bool(do_approximate_matching),
             "include_suppressed": bool(include_suppressed),
             }
        if context_name is not None:
            d['context_name'] = str(context_name)
        return self._call_api('tnrs/match_names', data=d, demand_success=False)

    def tree_of_life_about(self):
        return self._call_api('tree_of_life/about')

    def tree_of_life_induced_subtree(self, node_ids=None, ott_ids=None, label_format="name_and_id"):
        d = {"label_format": label_format.lower().strip()}
        if not (node_ids or ott_ids):
            raise ValueError("Either node_ids or ott_ids must be provided")
        if node_ids:
            d["node_ids"] = [str(i) for i in node_ids]
        if ott_ids:
            d["ott_ids"] = [int(i) for i in ott_ids]
        return self._call_api('tree_of_life/induced_subtree', data=d, demand_success=False)

    def tree_of_life_mrca(self, node_ids=None, ott_ids=None):
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
        cdict = {"node_ids": node_ids, "node_id": node_id, "ott_id": ott_id}
        name, value = self._one_and_only_one('tree_of_life/node_info', cdict)
        if name == "node_ids":
            d["node_ids"] = [str(i) for i in value]
        elif name == "ott_id":
            d["ott_id"] = int(value)
        else:
            assert name == "node_id"
            d["node_id"] = str(value)
        return self._call_api('tree_of_life/node_info', data=d, demand_success=False)

    def tree_of_life_subtree(self, node_id=None, ott_id=None,
                             tree_format="newick", label_format="name_and_id",
                             height_limit=None):
        d = {"format": str(tree_format), "label_format": str(label_format)}
        if height_limit is not None:
            d["height_limit"] = int(height_limit)
        if node_id is not None:
            d['node_id'] = str(node_id)
        elif ott_id is not None:
            d['ott_id'] = int(ott_id)
        else:
            raise ValueError("Either node_id or ott_id must be given to tree_of_life/subtree")
        return self._call_api('tree_of_life/subtree', data=d, demand_success=False)


def ot_datetime_str_to_object(xdatestr):
    return datetime.strptime(xdatestr, '%Y-%m-%d %H:%M:%S')
