import unittest
import os
import sys

from contextlib import contextmanager
from StringIO import StringIO

from Aggregator import Aggregator
import Mobigen.Common.Log as Log; Log.Init()

@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err

class TestAggregator(unittest.TestCase):
    """
        @brief test case using unittest.TestCase
    """
    def setUp(self):
        """
            @brief this method is called before every test methods
        """
        self.obj = Aggregator("Aggregator.py","TEST1", "conf/Aggregator.conf")

    def tearDown(self):
        """
            @brief this method is called after every test methods
        """
        pass

    def test_get_conf_parser_else1(self):
        with self.assertRaises(SystemExit) as cm:
            tmp_obj = Aggregator("Aggregator.py", "TEST1", "UnknownPath")
        self.assertEqual(cm.exception.code, None)

    def test_set_config_if1(self):
        with self.assertRaises(SystemExit) as cm:
            tmp_obj = Aggregator("Aggregator.py", "TEST1",
                    "tests/test_conf/Aggregator_no_groupby.conf")
        self.assertEqual(cm.exception.code, None)

    def test_set_config_try(self):
        with self.assertRaises(SystemExit) as cm:
            tmp_obj = Aggregator("Aggregator.py", "TEST1",
                    "tests/test_conf/Aggregator_no_db_confpath.conf")
        self.assertEqual(cm.exception.code, None)

    def test_set_config_except(self):
        with self.assertRaises(SystemExit) as cm:
            tmp_obj = Aggregator("Aggregator.py", "TEST1",
                    "tests/test_conf/Aggregator_db_exception.conf")
        self.assertEqual(cm.exception.code, None)

    def test_make_aggdict(self):
        expected_result = {'CAEP': ['sum', 'max', 'min', 'count']}
        self.assertEqual(self.obj.agg, expected_result)

    def test_load_MySQL(self):
        self.obj.run

    def test_load_Oracle(self):
        pass

    def test_load_non_existence(self):
        pass

    def test_load_except(self):
        pass

    def test_aggregate_ok(self):
        pass


if __name__ == '__main__':
    unittest.main()

