#!/usr/bin/env python3

class SourceSupportCollection(object):
    def __init__(self, supp_descrip, src_id_map):
        pass

class DictWrapper(object):
    def __init__(self, raw_dict):
        self._raw_dict = raw_dict

    def _move_to_attribute(self, attr_name, conv_fn=None):
        val = self._raw_dict.get(attr_name)
        if (val is not None) and (conv_fn is not None):
            val = conv_fn(val)
        setattr(self, '_{}'.format(attr_name), val)
        return val

    def _access_or_move(self, attr_name, conv_fn=None):
        wattr = '_{}'.format(attr_name)
        val = getattr(self, wattr)
        if val is None:
            return self._move_to_attribute(attr_name, conv_fn=conv_fn)
        return val

def wrap_list_elements(container, wrapper_class):
    return [wrapper_class(i) for i in container]

def wrap_ott_id_list_as_taxon(container):
    return wrap_list_elements([{'ott_id': i} for i in container], OTTaxonRef)

def wrap_list_of_dicts_as_ot_taxon_ref(container):
    return wrap_list_elements(container, OTTaxonRef)

class OTTaxonRef(DictWrapper):
    def __init__(self, taxon_dict):
        super(OTTaxonRef, self).__init__(taxon_dict)
        self._name = None
        self._ott_id = None
        self._rank = None
        self._tax_sources = None
        self._unique_name = None
        self._flags = None
        self._is_suppressed = None
        self._is_suppressed_from_synth = None
        self._source = None
        self._terminal_descendants = None
        self._lineage = None
        self._children = None
        self._fetched = set()

    def _access_fetch_or_move(self, attr_name, conv_fn=None, **kwargs):
        v = self._access_or_move(attr_name, conv_fn=conv_fn)
        if v is None and (attr_name not in self._fetched):
            from .ot_object import default_open_tree_obj
            OT = default_open_tree_obj()
            rd = OT.taxon_info(self.ott_id, **kwargs)
            self._raw_dict.update(rd.response_dict)
            v = self._access_or_move(attr_name, conv_fn=conv_fn)
            self._fetched.add(attr_name)
        return v

    @property
    def name(self):
        return self._access_or_move('name')

    @property
    def ott_id(self):
        return self._access_or_move('ott_id')

    @property
    def rank(self):
        return self._access_or_move('rank')

    @property
    def tax_sources(self):
        return self._access_or_move('tax_sources')

    @property
    def unique_name(self):
        return self._access_or_move('unique_name')

    @property
    def flags(self):
        return self._access_fetch_or_move('flags')

    @property
    def is_suppressed(self):
        return self._access_fetch_or_move('is_suppressed')

    @property
    def is_suppressed_from_synth(self):
        return self._access_fetch_or_move('is_suppressed_from_synth')

    @property
    def source(self):
        return self._access_fetch_or_move('source')

    @property
    def lineage(self):
        return self._access_fetch_or_move('lineage',
                                          include_lineage=True,
                                          conv_fn=wrap_list_of_dicts_as_ot_taxon_ref)

    @property
    def children(self):
        return self._access_fetch_or_move('children',
                                          include_children=True,
                                          conv_fn=wrap_list_of_dicts_as_ot_taxon_ref)

    @property
    def terminal_descendants(self):
        return self._access_fetch_or_move('terminal_descendants',
                                          include_terminal_descendants=True,
                                          conv_fn=wrap_ott_id_list_as_taxon)

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
        self._lineage = ndd.get('lineage', [])
        self._lineage_converted = False

    @property
    def lineage(self):
        if self._lineage and (not self._lineage_converted):
            self._lineage = [SynthNodeReference(i) for i in self._lineage]
            self._lineage_converted = True
        return self._lineage
