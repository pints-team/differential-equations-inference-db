"""Test the code from load_data.py.
"""

import unittest
import numpy as np
import pystreamflow


class TestLoadData(unittest.TestCase):

    def test_load_data(self):
        data = pystreamflow.load_data('03451500')

        # Test that all columns are present
        expected_columns = ['year', 'month', 'day', 'precipitation',
                            'evaporation', 'streamflow', 'max_temp',
                            'min_temp']
        self.assertEqual(list(data.columns), expected_columns)

        # Test the length of the data
        self.assertEqual(len(data), 2557)

        # Test that numeric data was loaded into the expected numpy types
        self.assertEqual(data.dtypes[0], np.int64)
        self.assertEqual(data.dtypes[3], np.float64)
