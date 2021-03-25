"""Test the code from model.py and ode.c.
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
        f = pystreamflow.ode.flux(s, a)
        self.assertAlmostEqual(f, expected)

        # Test with near zero value of a
        a = 1e-20
        s = 0.5
        expected = 0.5
        f = pystreamflow.ode.flux(s, a)
        self.assertAlmostEqual(f, expected)


class TestRHS(unittest.TestCase):

    def test_rhs(self):
        # Test the ode function
        params = [2.5, 100, 7, 1, -0.5, 60, 3.25, 0, 50]

        # Test with completely dry conditions. There should be no change in any
        # component
        y = [0.0] * 4
        f = pystreamflow.ode.ode_rhs(0, *y, 0, 1.0, *params)
        self.assertEqual(f, [0.0] * 5)
        self.assertGreaterEqual(f[4], 0.0)

        # Test that precipitation enters the interception component
        f = pystreamflow.ode.ode_rhs(0, *y, 10.0, 1.0, *params)
        self.assertAlmostEqual(f[0], 10.0)
        self.assertGreaterEqual(f[4], 0.0)

        # Test that with full interception storage, all precipitation enters
        # unsaturated storage
        y = [2.5, 0.0, 0.0, 0.0]
        f = pystreamflow.ode.ode_rhs(0, *y, 5.0, 1.0, *params)
        self.assertAlmostEqual(f[1], 5.0)
        self.assertGreaterEqual(f[4], 0.0)

        # Test effect of slow time constant
        y = [0.5] * 4
        params1 = [2.5, 100, 7, 1, -0.5, 10, 3.25, 0, 50]
        params2 = [2.5, 100, 7, 1, -0.5, 1000, 3.25, 0, 50]
        f1 = pystreamflow.ode.ode_rhs(0, *y, 5.0, 1.0, *params1)
        f2 = pystreamflow.ode.ode_rhs(0, *y, 5.0, 1.0, *params2)
        self.assertGreaterEqual(f2[2], f1[2])

        # Test effect of fast time constant
        y = [0.5] * 4
        params1 = [2.5, 100, 7, 1, -0.5, 10, 3.2, 0, 50]
        params2 = [2.5, 100, 7, 1, -0.5, 10, 32.0, 0, 50]
        f1 = pystreamflow.ode.ode_rhs(0, *y, 5.0, 1.0, *params1)
        f2 = pystreamflow.ode.ode_rhs(0, *y, 5.0, 1.0, *params2)
        self.assertGreaterEqual(f2[3], f1[3])
