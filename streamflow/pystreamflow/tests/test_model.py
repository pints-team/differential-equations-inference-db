"""Test the code from model.py and ode.c.
"""

import math
from importlib import reload
import sys
import unittest
import unittest.mock
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


class TestRiverModel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.input_times = [1, 2, 3, 4, 5, 6, 7]
        cls.precip = [0, 10, 0, 20, 20, 0, 1]
        cls.evap = [3, 3.5, 4, 4.5, 5, 5.5, 5.5]

    def test_init(self):
        # Test initialization
        pystreamflow.RiverModel(self.input_times, self.precip, self.evap)

    def test_n_parameters(self):
        m = pystreamflow.RiverModel(self.input_times, self.precip, self.evap)
        self.assertEqual(m.n_parameters(), 7)

    def test_set_model_data(self):
        m = pystreamflow.RiverModel(self.input_times, self.precip, self.evap)

        self.assertEqual(m.model_data_times, self.input_times)
        self.assertEqual(m.rainfall_data, self.precip)
        self.assertEqual(m.evap_data, self.evap)

        self.assertEqual(m.rainfall_data_dict[1], 0)
        self.assertEqual(m.evap_data_dict[1], 3)

        self.assertEqual(m.rainfall_data_dict[7], 1)
        self.assertEqual(m.evap_data_dict[7], 5.5)

    def test_simulate(self):
        # Test running simulate
        params = [2.5, 100, 7, 1, -0.5, 60, 3.25]
        times = [4, 5, 6]
        m = pystreamflow.RiverModel(self.input_times, self.precip, self.evap)
        y = m.simulate(params, times)
        self.assertEqual(len(y), 3)

        m = pystreamflow.RiverModel(
            self.input_times, self.precip, self.evap, solver='scikit')
        y = m.simulate(params, times)
        self.assertEqual(len(y), 3)

    def test_no_data(self):
        # Test trying to simulate where data has not been provided
        params = [2.5, 100, 7, 1, -0.5, 60, 3.25]
        times = [10, 11, 12]
        m = pystreamflow.RiverModel(self.input_times, self.precip, self.evap)

        with self.assertRaises(RuntimeError) as e:
            m.simulate(params, times)
        self.assertTrue('data are not available' in str(e.exception))

    def test_solvers(self):
        # Test when the scikit solver is not available
        with unittest.mock.patch.dict(sys.modules):
            sys.modules['scikits.odes'] = None
            reload(sys.modules['pystreamflow.model'])

            with self.assertRaises(RuntimeError) as e:
                pystreamflow.RiverModel(
                    self.input_times, self.precip, self.evap, solver='scikit')
            self.assertTrue('scikit solver could not be' in str(e.exception))
