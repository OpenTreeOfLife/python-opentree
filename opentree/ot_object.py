"""OT object. High level wrapper for OpenTree calls"""
#!/usr/bin/env python3
import sys

from .ws_wrapper import (OTWebServicesError,
                         WebServiceRunMode,
                         )
from .ot_ws_wrapper import OTWebServiceWrapper

# from .nexson_helpers import extract_tree_nexson, extract_otu_nexson, detect_nexson_version

FILES_SERVER_URL = 'files'


class FilesServerWrapper(OTWebServiceWrapper):
    """
    This class provides a mid-level wrapper for interaction with OT web services and data.
    """
    def __init__(self, api_endpoint=FILES_SERVER_URL, run_mode=WebServiceRunMode.RUN):
        super(FilesServerWrapper, self).__init__(api_endpoint=api_endpoint, run_mode=run_mode)

    def get_subproblem_scaffold_tree(self, synth_id):
        url_frag = 'synthesis/{s}/{s}/subproblems/subproblems-scaffold-only.tre'.format(s=synth_id)
        return self._call_api(url_frag, http_method='GET', headers='text')

    def get_subproblem_size_info(self, synth_id):
        url_frag = 'synthesis/{s}/{s}/subproblems/subproblem_size_summary.json'.format(s=synth_id)
        return self._call_api(url_frag, http_method='GET')

    def get_subproblem_solution(self, synth_id, ott_id):
        url_frag = 'synthesis/{s}/{s}/subproblem_solutions/ott{o}.tre'.format(s=synth_id,
                                                                              o=ott_id)
        return self._call_api(url_frag, http_method='GET', headers='text')

    def get_reversed_subproblem_solution(self, synth_id, ott_id):
        url_frag = 'synthesis/{s}/{s}/reversed_subproblem_solutions/ott{o}.tre'.format(s=synth_id,
                                                                                       o=ott_id)
        return self._call_api(url_frag, http_method='GET', headers='text')

    def get_subproblem_trees(self, synth_id, ott_id):
        url_frag = 'synthesis/{s}/{s}/subproblems/ott{o}.tre'.format(s=synth_id, o=ott_id)
        return self._call_api(url_frag, http_method='GET', headers='text')


_default_api_endpoint = None
_default_run_mode = None


def default_open_tree_obj():
    global _default_api_endpoint, _default_run_mode
    if _default_api_endpoint is None:
        _default_api_endpoint = 'production'
        _default_run_mode = WebServiceRunMode.RUN
    return OpenTree(api_endpoint=_default_api_endpoint,
                    run_mode=_default_run_mode)


class OpenTree(object):
    """
    This class provides a high-level wrapper for interaction with OT web services and data.
    The method names are intended to be clear to a wide variety of users, rather than
    necessarily matching the API calls directly.
    """

    def __init__(self, api_endpoint='production', run_mode=WebServiceRunMode.RUN):
        global _default_api_endpoint, _default_run_mode
        if _default_api_endpoint is None:
            _default_api_endpoint = api_endpoint
            _default_run_mode = run_mode
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
        """
        Get information about the Open Tree of Life taxonomy and the synthetic tree.
        """
        tax_about = self.ws.taxonomy_about().response_dict
        tree_about = self.ws.tree_of_life_about().response_dict
        return {'taxonomy_about': tax_about,
                'synth_tree_about': tree_about
                }

    def get_study(self, study_id):
        """
        Get citation of a study and its associated metadata.

        Parameters
        ----------
        study_id : single character value
            The study id from Open Tree of Life.
        """
        return self.ws.study(study_id)

    def get_tree(self, study_id, tree_id,
                 tree_format="nexson", label_format="ot:originallabel", demand_success=False):
        """
        Get a source tree from phylesystem and its associated metadata.

        Parameters
        ----------
        study_id : single character value
            The study id from Open Tree of Life.
        tree_id : single character value
            The tree id of a tree within the study id provided.
        tree_format : single character value
            Must be one of "newick", "nexson", "nexus", or "object"
            If tree format is newick or nexus, returns tree as string in that format.
            If "nexson", returns semi-useless tree nexson w/o OTUS.
        label_format : single character value
            Must be one of "ot:originallabel", "ot:ottid", or "ot:otttaxonname".
            "ot:originallabel" returns the tree with tip labels as it was originally
              submitted to phylesystem by a curator.
            "ot:ottid" returns a tree with tip labels corresponding to the matching
              ott id.
            "ot:otttaxonname" returns a tree with tip labels corresponding to the
              matching ott taxon name.
        demand_success : boolean
            Whether to return an error or return a somewhat failed output silently.
        """
        if tree_format not in ["newick", "nexson", "nexus", "object"]:
            raise ValueError('"{}" not recognized as a valid tree_format'.format(tree_format))
        if tree_format == 'object':
            ws_rec = self.ws.study(study_id, demand_success=False)

            def efn(rd):
                nexs = rd['data']
                return ws_rec._to_object_converter.tree_from_nexson(nexs,
                                                                    tree_id=tree_id,
                                                                    label_format=label_format)

            ws_rec._tree_from_response_extractor = efn
        else:
            ws_rec = self.ws.tree(study_id, tree_id, tree_format, label_format, demand_success)
            from .ws_wrapper import extract_content_from_raw_text_method_dict
            if tree_format in ('newick', 'nexus'):
                ws_rec._tree_from_response_extractor = extract_content_from_raw_text_method_dict
        return ws_rec

    def get_otus(self, study_id):
        """
        Get OTUs from a study in the Open Tree of Life Phylesystem.

        Parameters
        ----------
        study_id : single character value
            The study id from Open Tree of Life.
        """
        return self.ws.otus(study_id)

    def conflict_info(self, study_id, tree_id, compare_to='synth'):
        """
        Get node status data from any tree in the Open Tree of Life Phylesystem.

        Parameters
        ----------
        study_id : single character value
            The study id from Open Tree of Life.
        tree_id : single character value
            The tree id of a tree within the study id provided.
        compare_to : a single character value
            Usually, you want this to be 'synth', to compare to the synthetic tree.
            Alternatively, you can compare your tree to any other tree in phylesystem.
        """
        return self.ws.conflict(study_id, tree_id, compare_to, demand_success=False)

    def conflict_str(self, tree_str, compare_to='synth'):
        """
        Get node status data from a newick string tree with ott_ids as labels, following the rough
        format:
        "(('_nd1_ott770315','newick_nd2_ott417950')'_nd3_','_nd4_ott158484')'_nd5';".

        Parameters
        ----------
        tree_str: a tree in 'conflict formatted' newick string
        compare_to : a single character value
            Usually, you want this to be 'synth', to compare to the synthetic tree.
            Alternatively, you can compare your tree to any other tree in phylesystem.
        """
        return self.ws.conflict_from_newick(tree_str, compare_to, demand_success=False)

    def studies_properties(self):
        """
        Get properties that can be used to search across studies and trees in phylesystem.
        """
        return self.ws.studies_properties()

    def find_studies(self, value, search_property, exact=False, verbose=False):
        """
        Get study ids that match a certain value of a given search property.

        Parameters
        ----------
        value : single character value
            The study id from Open Tree of Life.
        search_property : single character value
            Any value from studies_properties.
        exact : boolean

        verbose : boolean
        """
        return self.ws.studies_find_studies(value, search_property=search_property,
                                            exact=exact, verbose=verbose)

    def find_trees(self, value, search_property, exact=False, verbose=False):
        """
        Get trees that match a certain value of a given search property.

        Parameters
        ----------
        value : single character value
            The study id from Open Tree of Life.
        search_property : single character value
            Any value from studies_properties.
        exact : boolean

        verbose : boolean

        Example
        -------


        """
        return self.ws.studies_find_trees(value, search_property=search_property,
                                          exact=exact, verbose=verbose)

    def taxon_info(self, ott_id=None, source_id=None, include_lineage=False,
                   include_children=False, include_terminal_descendants=False):
        """
        Get taxonomic information for a given taxon in the Open Tree taxonomy.

        Parameters
        ----------
        ott_id : single character value
            The OTT id of a taxon.
        source_id : maybe single character value

        include_lineage : boolean

        include_children : boolean

        include_terminal_descendant : boolean
        """
        return self.ws.taxonomy_taxon_info(ott_id=ott_id, source_id=source_id,
                                           include_lineage=include_lineage,
                                           include_children=include_children,
                                           include_terminal_descendants=include_terminal_descendant)

    def taxon_mrca(self, ott_ids=None, ignore_unknown_ids=True):
        """
        Get the node corresponding to the most recent commom ancestor (mrca) of
          a taxon in the synthetic Open Tree of Life tree.
        Notes from Luna:
            Does it work with just one id?
            Since it is not always a taxon mrca, should it be called get_mrca?

        Parameters
        ----------
        ott_ids : maybe single character value
        ignore_unknown_ids : boolean
            Default to TRUE.
        """
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
        """Get a subtree of a particular taxon
        """
        return self.ws.taxonomy_subtree(ott_id=ott_id, label_format=label_format)

    def tnrs_contexts(self):
        """Get a list of taxonomic contexts that can be used to constraint a TNRS match.
        """
        return self.ws.tnrs_contexts()

    def tnrs_infer_context(self, names):
        """Infer taxonomic context for names via a TNRS (Taxonomic Name Resolution Service) match.
        """
        return self.ws.tnrs_infer_context(names)

    def tnrs_match(self, names, context_name=None, do_approximate_matching=False,
                   include_suppressed=False):
        """Match taxon names to Open Tree Taxonomy using TNRS (Taxonomic Name Resolution
             Service).
        """
        return self.ws.tnrs_match_names(names, context_name=context_name,
                                        do_approximate_matching=do_approximate_matching,
                                        include_suppressed=include_suppressed)

    def tnrs_autocomplete(self, name, context_name=None, include_suppressed=False):
        """Taxonomic name resolution service autocomplete
        """
        return self.ws.tnrs_autocomplete_name(name, context_name=context_name,
                                              include_suppressed=include_suppressed)

    def synth_node_info(self, node_ids=None, node_id=None, ott_id=None, include_lineage=False):
        """Get information of a node
        """
        return self.ws.tree_of_life_node_info(node_ids=node_ids, node_id=node_id, ott_id=ott_id,
                                              include_lineage=include_lineage)

    def synth_subtree(self, node_id=None, ott_id=None,
                      tree_format="newick", label_format="name_and_id",
                      height_limit=None):
        """Get a subtree
        """
        return self.ws.tree_of_life_subtree(node_id=node_id, ott_id=ott_id,
                                            tree_format=tree_format,
                                            label_format=label_format,
                                            height_limit=height_limit)

    def synth_induced_tree(self, node_ids=None,
                           ott_ids=None, label_format="name_and_id",
                           ignore_unknown_ids=True):
        """Get an induced subtree
        """
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
            msgtemplate = 'Call to tree_of_life/induced_subtree failed with the message "{}"'
            self._cull_unknown_ids_from_args(call_record, node_ids, ott_ids)

    def synth_mrca(self, node_ids=None, ott_ids=None, ignore_unknown_ids=True):
        """Get the most recent common ancestor of a group of taxa on the synthetic
             Open Tree of Life
        """
        while True:
            assert (ott_ids or node_ids)
            call_record = self.ws.tree_of_life_mrca(node_ids=node_ids,
                                                    ott_ids=ott_ids)
            if call_record:
                return call_record
            if not ignore_unknown_ids:
                msgtemplate = 'Call to tree_of_life/mrca failed with the message "{}"'
                message = call_record.response_dict['message']
                raise OTWebServicesError(msgtemplate.format(message))
            self._cull_unknown_ids_from_args(call_record, node_ids, ott_ids)
            if not ott_ids or node_ids:
                msgtemplate = 'Call to tree_of_life/mrca failed as all ids were pruned'
                raise OTWebServicesError(msgtemplate)

    # noinspection PyMethodMayBeStatic
    def _cull_unknown_ids_from_args(self, call_record, node_ids, ott_ids):
        """Cull unknown ids from arguments
        """
        assert ('unknown' in call_record.response_dict), call_record.response_dict
        unknown_ids = call_record.response_dict['unknown']
        for u in unknown_ids:
            if node_ids and u in node_ids:
                node_ids.remove(u)
            else:
                assert u.startswith('ott')
                ui = int(u[3:])
                if ott_ids and (ui in ott_ids):### What if it is a astinrg
                    ott_ids.remove(ui)
                if ott_ids and (str(ui) in ott_ids):### What if it is a astinrg
                    ott_ids.remove(ui)

    def get_ottid_from_gbifid(self, gbif_id):
        """Returns an ott id for a gbif id
        ott_id is set to 'None' if the gbif id is not found in the Open Tree Taxanomy
        """
        assert int(gbif_id)
        gbiftax = "gbif:{}".format(int(gbif_id))
        res = self.taxon_info(source_id=gbiftax)
        if res.status_code == 200:
            ott_id = int(res.response_dict['ott_id'])
            return ott_id
        if res.status_code == 400:
            return None
        msgtemplate = 'Call to taxon_info failed with the message "{}"'
        message = res.response_dict['message']
        raise OTWebServicesError(msgtemplate.format(message))

    def get_citations(self, studies):
        """Returns study citations from a list of study or tree ids
        """
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
                cites.append(opentree_url + '\n' +
                             new_cite[0].get('ot:studyPublicationReference', '')
                             + '\n' +
                             new_cite[0].get('ot:studyPublication', '') + '\n')
        return "\n".join(cites)

    def get_ottid_from_name(self, spp_name, exact=True):
        """Returns an ott id for a string
        ott_id is set to 'None' if the gbif id is not found in the Open Tree Txanomy
        """
        res = self.tnrs_match([spp_name], do_approximate_matching=not exact)
        if res.status_code == 200:
            if len(res.response_dict['results']) > 0:
                if res.response_dict['results'][0]['matches'] == None:
                    return None
                ott_id = int(res.response_dict['results'][0]['matches'][0]['taxon']['ott_id'])
                return ott_id
            return None
        msgtemplate = 'Call to tnrs_match failed with the message "{}"'
        message = res.response_dict['message']
        raise OTWebServicesError(msgtemplate.format(message))

    def get_matchdict_from_taxlist(self, list_of_taxa):
        """
        Input: a list of taxon names
        Returns: matches - a dictionary of name:ott_id
        and failed - a set of the names that were not found.
        """
        matches = dict()
        failed = set()
        for tax in list_of_taxa:
            tax = tax.strip()
            if tax != '':
                try:
                    ott_id = self.get_ottid_from_name(tax)
                    matches[tax] = 'ott{}'.format(ott_id)
                except IndexError:
                    failed.add(tax)
                    sys.stderr.write("Failed to get an ottid for {}".format(tax))
        return matches, failed