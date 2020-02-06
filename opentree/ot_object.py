#!/usr/bin/env python3

from .ws_wrapper import (OTWebServicesError,
                         WebServiceRunMode,
                         )
from .ot_ws_wrapper import OTWebServiceWrapper

FILES_SERVER_URL = 'files'


class FilesServerWrapper(OTWebServiceWrapper):
    def __init__(self, api_endpoint=FILES_SERVER_URL, run_mode=WebServiceRunMode.RUN):
        super(FilesServerWrapper, self).__init__(api_endpoint=api_endpoint, run_mode=run_mode)

    def get_subproblem_scaffold_tree(self, synth_id):
        url_frag = 'synthesis/{s}/{s}/subproblems/subproblems-scaffold-only.tre'.format(s=synth_id)
        return self._call_api(url_frag, http_method='GET', headers='text')

    def get_subproblem_size_info(self, synth_id):
        url_frag = 'synthesis/{s}/{s}/subproblems/subproblem_size_summary.json'.format(s=synth_id)
        return self._call_api(url_frag, http_method='GET')

    def get_subproblem_solution(self, synth_id, ott_id):
        url_frag = 'synthesis/{s}/{s}/subproblem_solutions/ott{o}.tre'.format(s=synth_id, o=ott_id)
        return self._call_api(url_frag, http_method='GET', headers='text')

    def get_reversed_subproblem_solution(self, synth_id, ott_id):
        url_frag = 'synthesis/{s}/{s}/reversed_subproblem_solutions/ott{o}.tre'.format(s=synth_id, o=ott_id)
        return self._call_api(url_frag, http_method='GET', headers='text')

    def get_subproblem_trees(self, synth_id, ott_id):
        url_frag = 'synthesis/{s}/{s}/subproblems/ott{o}.tre'.format(s=synth_id, o=ott_id)
        return self._call_api(url_frag, http_method='GET', headers='text')


class OpenTree(object):
    """
    This class provides a high-level wrapper for interaction with OT web services and data.
    The method names are intended to be clear to a wide variety of users, rather than necessarily matching
    the API calls directly.
    """

    def __init__(self, api_endpoint='production', run_mode=WebServiceRunMode.RUN):
        self._api_endpoint = api_endpoint
        self._run_mode = run_mode
        self._ws = None
        self._files_server = None

    @property
    def files_server(self):
        if self._files_server is None:
            self._files_server = FilesServerWrapper(run_mode=self._run_mode)
        return self._files_server

    @property
    def ws(self):
        if self._ws is None:
            self._ws = OTWebServiceWrapper(api_endpoint=self._api_endpoint,
                                           run_mode=self._run_mode)
        return self._ws

    def get_subproblem_scaffold_tree(self, synth_id):
        return self.files_server.get_subproblem_scaffold_tree(synth_id)

    def get_subproblem_size_info(self, synth_id):
        return self.files_server.get_subproblem_size_info(synth_id)

    def get_subproblem_solution(self, synth_id, ott_id):
        return self.files_server.get_subproblem_solution(synth_id, ott_id)

    def get_subproblem_trees(self, synth_id, ott_id):
        return self.files_server.get_subproblem_trees(synth_id, ott_id)

    def get_reversed_subproblem_solution(self, synth_id, ott_id):
        return self.files_server.get_reversed_subproblem_solution(synth_id, ott_id)

    def about(self):
        tax_about = self.ws.taxonomy_about()
        tree_about = self.ws.tree_of_life_about()
        return {'taxonomy_about': tax_about,
                'synth_tree_about': tree_about
                }

    def get_study(self, study_id):
        return self.ws.study(study_id)

    def get_tree(self, study_id, tree_id, tree_format="nexson", label_format="ot:originallabel", demand_success = False):
        """
        Gets a tree from phylesystem.

        Parameters
        ----------

        study_id : single character value.
            The study id from Open Tree of Life.
        tree_id : single character value.
            The tree id of a tree within the study id provided.
        tree_format : single character value.
            Must be one of "newick", "nexson", or "nexus".
            If tree format is newick or nexus, returns tree as string in that format.
            If "nexson", returns semi-useless tree nexson w/o OTUS.
        label_format : single character value.
        demand_success : boolean.
            Wether to return an error or return an error message silently.
        """
        assert tree_format in ["newick", "nexson", "nexus"]
        output = self.ws.tree(study_id, tree_id, tree_format, label_format, demand_success)
        if tree_format != "nexson":
            return output.response_dict["content"].decode()

        else:
            return output

    def get_otus(self, study_id):
        return self.ws.otus(study_id)

#TODO for Luna :)
    def conflict_info(self, study_id, tree_id, compare_to = 'synth'):
        return self.ws.conflict(study_id, tree_id, compare_to, demand_success = False)

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

    def get_ottid_from_gbifid(self, gbif_id):
        """Returns an ott id for a gbif id
        ott_id is set to 'None' if the gbif id is not found in the Open Tree Txanomy
        """
        assert int(gbif_id)
        gbiftax = "gbif:{}".format(int(gbif_id))
        res = self.taxon_info(source_id=gbiftax)
        if res.status_code == 200:
            ott_id = int(res.response_dict['ott_id'])
            return ott_id
        elif res.status_code == 400:
            return None
        else:
            msgtemplate = 'Call to taxon_info failed with the message "{}"'
            message = res.response_dict['message']
            raise OTWebServicesError(msgtemplate.format(message))

    def get_citations(self, studies):
        """Returns a string with citation info for list of study or Tree Ids"""
        cites = []
        for study in studies:
            if '@' in study:
                studyid = study.split('@')[0]
                treeid = study.split('@')[1]
                opentree_url = "https://tree.opentreeoflife.org/curator/study/view/{}?tab=trees&tree={}"
                opentree_url = opentree_url.format(studyid, treeid)
            else:
                studyid = study
                opentree_url = "https://tree.opentreeoflife.org/curator/study/view/{}".format(studyid)
            studyres = self.find_studies(studyid, search_property='ot:studyId', verbose=True)
            new_cite = studyres.response_dict.get('matched_studies', None)
            if new_cite:
                cites.append(
                    opentree_url + '\n' + new_cite[0].get('ot:studyPublicationReference', '') + '\n' + new_cite[0].get(
                        'ot:studyPublication', '') + '\n')
        return "\n".join(cites)

    def get_ottid_from_name(self, spp_name, exact=True):
        """Returns an ott id for a string
        ott_id is set to 'None' if the gbif id is not found in the Open Tree Txanomy
        """
        res = self.tnrs_match([spp_name], do_approximate_matching=not exact)
        if res.status_code == 200:
            if len(res.response_dict['results']) > 0:
                ott_id = int(res.response_dict['results'][0]['matches'][0]['taxon']['ott_id'])
                return ott_id
            else:
                return None
        else:
            msgtemplate = 'Call to tnrs_match failed with the message "{}"'
            message = res.response_dict['message']
            raise OTWebServicesError(msgtemplate.format(message))
