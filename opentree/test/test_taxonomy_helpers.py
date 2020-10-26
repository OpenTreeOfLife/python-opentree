import unittest

from opentree import taxonomy_helpers

ott_loc = "../ott/"

class TestTaxonomyHelpers(unittest.TestCase):
    def test_get_taxonomy(self):
        tax_path = taxonomy_helpers.download_taxonomy_file(loc = ott_loc, version = "3.2")
        assert tax_path == ott_loc + "/ott3.2", tax_path
    def test_get_forward(self):
        tax_path = taxonomy_helpers.download_taxonomy_file(loc = ott_loc, version = "3.2")
        ott_ids = ['ott5859962', 'ott773110']
        forwards_file = tax_path + "/forwards.tsv"
        taxonomy_helpers.get_forwarded_ids(ott_ids=ott_ids, forwards_file=forwards_file)