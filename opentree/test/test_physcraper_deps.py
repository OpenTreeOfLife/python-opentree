import unittest

from opentree import OT

bad_study_id = "pg_873"
study_id = "ot_350"

class TestPhyscraperDeps(unittest.TestCase):
    def test_demands_id_arg(self):
        with self.assertRaises(TypeError):
            OT.get_study()

    def test_get_study_fail(self):
        study = OT.get_study(bad_study_id)
        assert study.response_dict == {'description': 'Study #{} GET failure'.format(bad_study_id), 'error': 1}


    def test_get_study(self):
        study = OT.get_study(study_id)
        assert 'data' in study.response_dict

if __name__ == '__main__':
    unittest.main()
