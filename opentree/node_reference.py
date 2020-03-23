#!/usr/bin/env python3

class SourceSupportCollection(object):
    def __init__(self, supp_descrip, src_id_map):
        pass

class OTTaxonRef(object):
    def __init__(self, taxon_dict):
        self.name = taxon_dict['name']
        self.ott_id = taxon_dict['ott_id']
        self.rank = taxon_dict.get('rank')
        self.tax_sources = taxon_dict.get('tax_sources', [])
        self.unique_name = taxon_dict.get('unique_name', self.name)

class SynthNodeReference(object):
    def __init__(self, node_descrip_dict):
        ndd = node_descrip_dict
        src_id_map = ndd.get('source_id_map', {})
        self.node_id = ndd['node_id']
        self.num_tips = ndd['num_tips']
        self.query = ndd.get('query')
        td = ndd.get('taxon', None)
        self.taxon = None if td is None else OTTaxonRef(td)
        SSC = SourceSupportCollection
        self.supported_by = SSC(ndd.get('supported_by', {}), src_id_map)
        self.conflicts_with = SSC(ndd.get('conflicts_with', {}), src_id_map)
        self.supported_by = SSC(ndd.get('supported_by', {}), src_id_map)
        self.resolves = SSC(ndd.get('resolves', {}), src_id_map)
        self.partial_path_of = SSC(ndd.get('partial_path_of', {}), src_id_map)
        self.terminal = SSC(ndd.get('terminal', {}), src_id_map)
        self._lineage = ndd.get('lineage')
