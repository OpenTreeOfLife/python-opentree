import unittest

from opentree import taxonomy_helpers

ott_loc = "../ott/"
corr_tax_path = ott_loc + "/ott3.2"

class TestTaxonomyHelpers(unittest.TestCase):
    def test_get_taxonomy(self):
        tax_path = taxonomy_helpers.download_taxonomy_file(loc = ott_loc, version = "3.2")
        assert tax_path == ott_loc + "/ott3.2", tax_path
    def test_get_forward(self):
        tax_path = taxonomy_helpers.download_taxonomy_file(loc = ott_loc, version = "3.2")
        ott_ids = ['ott5859962', 'ott773110']
        forwards_file = tax_path + "/forwards.tsv"
        taxonomy_helpers.get_forwarded_ids(ott_ids=ott_ids, forwards_file=forwards_file)
    def test_clean_taxonomy(self):
        cfi = taxonomy_helpers.clean_taxonomy_file(taxonomy_file="{}/taxonomy.tsv".format(corr_tax_path))
    def test_get_by_rank(self):
        ids = taxonomy_helpers.get_ott_ids_for_rank(rank="family", taxonomy_file="{}/taxonomy.tsv".format(corr_tax_path))
        assert len(ids) == 21979, len(ids)
    def test_get_by_group(self):
        aves = taxonomy_helpers.get_ott_ids_for_group(group_ott_id=81461)
        assert len(aves) == 27465, len(aves)
    def test_rank_in_taxon(self):
        bird_families = taxonomy_helpers.get_ott_ids_group_and_rank(group_ott_id=81461, rank='family', taxonomy_file="{}/taxonomy.tsv".format(corr_tax_path))
        assert len(bird_families) == 390, len(bird_genera)