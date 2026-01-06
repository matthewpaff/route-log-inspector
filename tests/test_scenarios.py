from pathlib import Path
import unittest

from scenarios import check_case, load_cases


class ScenarioTests(unittest.TestCase):
    def test_versioned_synthetic_cases(self):
        directory = Path(__file__).resolve().parents[1] / 'scenarios'
        for path, case in load_cases(directory):
            with self.subTest(case=path.name):
                check_case(case)
