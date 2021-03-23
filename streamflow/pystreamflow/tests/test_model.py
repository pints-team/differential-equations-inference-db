"""Test the code from model.py.
"""

import math
import unittest
import pystreamflow


class TestFlux(unittest.TestCase):

    def test_flux(self):
        # Test with float inputs
        a = 2.0
        s = 0.5
        expected = (1 - math.exp(-a * s)) / (1 - math.exp(-a))
        f = pystreamflow.flux(s, a)
        self.assertAlmostEqual(f, expected)

        # Test with near zero value of a
        a = 1e-20
        s = 0.5
        expected = 0.5
        f = pystreamflow.flux(s, a)
        self.assertAlmostEqual(f, expected)
