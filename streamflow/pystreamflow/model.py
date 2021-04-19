"""PINTS implementation of the rainfall runoff model.
"""

import math
import numpy as np
import scipy.integrate
import pints
import pystreamflow

# Try to import the optional scikit odes solver, and record whether or not it
# was available
try:
    import scikits.odes
    scikit_ode_avail = True
except ImportError:
    scikit_ode_avail = False


class RiverModel(pints.ForwardModel):
    """Rainfall runoff model of river streamflow.

    The model divides the movement of water through the river basin into the
    following spatially-grouped components representing different hydrological
    processes:

        * Interception, representing vegetation. Rainfall lands on vegetative
          surfaces such as leaves and stems, at which point it may either enter
          the ground or evaporate back into the air.
        * Unsaturated zone, representing the soil above the water table.

    From the unsaturated zone, water can enter the river flow via one of two
    processes:

        * A slow reservoir, representing percolation
        * A fast reservoir, representing surface runoff

    The model has four latent state variables, each giving the level of water
    in the components described above, which varies over time:

        * S_i = interception storage
        * S_u = unsaturated storage
        * S_s = slow reservoir
        * S_f = fast reservoir

    and one observed variable (in fact, it is dz/dt, or the streamflow, that is
    observed):

        * z = water flowed out of the river

    The behavior of all the variables is governed by a system of differential
    equations, namely

        * dS_i/dt = Precip(t) - InterceptEvap(t) - EffectPrecip(t)
        * dS_u/dt = EffectPrecip(t) - UnsatEvap(t) - Percolation(t) - Runoff(t)
        * dS_s/dt = Percolation(t) - SlowStream(t)
        * dS_f/dt = Runoff(t) - FastStream(t)
        * dz/dt = SlowStream(t) + FastStream(t)

    Each term is defined below. The model is characterized by the following
    unknown parameters:

        * I_max = maximum interception
        * S_u,max = unsaturated storage capacity
        * Q_s,max = maximum percolation
        * alpha_e = evaporation flux shape
        * alpha_f = runoff flux shape
        * K_s = slow reservoir time constant
        * K_f = fast reservoir time constant

    as well as the following two parameters whose values are here assumed fixed
    and known:

        * alpha_s = 0 (percolation flux shape)
        * alpha_i = 50 (interception flux shape)

    Appearing multiple times in the model is the flux function f, given by:

        * f(S, a) = (1 - exp(-a * S)) / (1 - exp(-a))

    Precip = measured precipitation (provided as input to the model)

    Evap = measured or theoretical evaporation (provided as input to the model)

    InterceptEvap = evaporation from the interception component

        * InterceptEvap(t) = Evap(t) * f(S_i / I_max, alpha_i)

    EffectPrecip = effective precipitation that gets sent to unsaturated
    storage

        * EffectPrecip(t) = Precip(t) * f(S_i / I_max, -alpha_i)

    UnsatEvap = evaporation from unsaturated storage

        * UnsatEvap(t) = max(0, Evap(t) - InterceptEvap(t))
                       * f(S_u / S_u,max, alpha_e)

    Percolation = trickling of water through the ground

        * Percolation(t) = Q_s,max * f(S_u / S_u,max, alpha_s)

    Runoff = flow of water on the surface

        * Runoff(t) = EffectPrecip(t) * f(S_u / S_u,max, alpha_f)

    SlowStream = The slow component of the river flow

        * SlowStream(t) = S_s / K_s

    FastStream = The fast component of the river flow

        * FastStream(t) = S_f / K_f

    This is the model that was studied in [1]_. See also [2]_, which contains
    further details for models of this type.

    See also the following MATLAB code
    https://github.com/Zaijab/DREAM/tree/master/examples/example_14

    References
    ----------
    .. [1] Schoups, G., & Vrugt, J. A. (2010). A formal likelihood function for
           parameter and predictive inference of hydrologic models with
           correlated, heteroscedastic, and non‐Gaussian errors. Water
           Resources Research, 46(10).
    .. [2] Schoups, G., Vrugt, J. A., Fenicia, F., & van de Giesen, N. C.
           (2010). Inaccurate numerical implementation of conceptual hydrologic
           models corrupts accuracy and efficiency of MCMC simulation. Water
           Resources Research, 46, W10530.
    """
    def __init__(self,
                 times,
                 rainfall,
                 evaporation,
                 solver='scipy',
                 rtol=1e-7,
                 atol=1e-7):
        """
        Parameters
        ----------
        times : list
            Time points corresponding to the rainfall and evaporation data
        rainfall : list
            Daily rainfall measurements
        evaporation : list
            Daily evaporation measurements
        solver : {'scipy', 'scikit'}, optional ('scipy')
            Which ODE solver library to use. 'scipy' corresponds to the
            scipy.integrate.solve_ivp function. 'scikit' uses scikits.odes.
            Note that scikits.odes is an optional dependency which must be
            available for this option to work.
        rtol : float
            Relative tolerance for the ODE solver
        atol : float
            Absolute tolerance for the ODE solver
        """
        super().__init__()

        self.set_model_data(times, rainfall, evaporation)

        # Initial conditions
        # Set all the variables to a small value. To eliminate the effect of
        # the initial condition, the model should be run for some time before
        # comparing its output to data.
        S_i = 1e-6
        S_u = 1e-6
        S_s = 1e-6
        S_f = 1e-6
        z = 1e-6
        self.init_cond = [S_i, S_u, S_s, S_f, z]

        # Solver properties
        self.solver = solver
        self.rtol = rtol
        self.atol = atol

        # Check that scikit is available
        if self.solver == 'scikit' and not scikit_ode_avail:
            raise RuntimeError('scikit solver could not be imported')

    def n_parameters(self):
        return 7

    def set_model_data(self, times, rainfall, evaporation):
        """Set the rainfall and evaporation data.

        Parameters
        ----------
        times : list
            Time points corresponding to the rainfall and evaporation data
        rainfall : list
            Daily rainfall measurements
        evaporation : list
            Daily evaporation measurements
        """
        self.model_data_times = times
        self.rainfall_data = rainfall
        self.evap_data = evaporation

        self.rainfall_data_dict = dict(zip(times, rainfall))
        self.evap_data_dict = dict(zip(times, evaporation))

    def simulate(self, parameters, times):
        """Run a forward simulation.

        It uses the rainfall and evaporation data saved inside this model
        object.

        Parameters
        ----------
        parameters : list
            [I_max, S_umax, Q_smax, alpha_e, alpha_f, K_s, K_f]
        times : list
            Time points on which to evaluate the solution

        Returns
        -------
        np.array
            Solution for river streamflow at the given times and parameters
        """
        # Check that the time range has data
        if min(times) < min(self.model_data_times) or \
                max(times) > max(self.model_data_times):
            raise RuntimeError('Rainfall and evaporation data are not '
                               'available at these time points.')

        # Set values for fixed parameters
        alpha_s = 0.0
        alpha_i = 50

        # Get the starting day for model data
        first_model_data_time = min(self.model_data_times)

        if self.solver == 'scipy':
            # Define derivative function for solver
            def f(t, y):
                precip = self.rainfall_data_dict.get(math.ceil(t), 0)
                evap = self.evap_data_dict.get(math.ceil(t), 0)
                return pystreamflow.ode.ode_rhs(
                            t,
                            *y[:-1],
                            precip,
                            evap,
                            *parameters,
                            alpha_s,
                            alpha_i)

            # Solve the equation
            t_range = (min(first_model_data_time, min(times)), max(times))
            res = scipy.integrate.solve_ivp(
                f,
                t_range,
                self.init_cond,
                t_eval=[times[0]-1] + list(times),
                rtol=self.rtol,
                atol=self.atol,
                method='RK23'
            )

            # Get the flow component
            y = list(res.y[4])

        elif self.solver == 'scikit':
            # Define derivative function for solver
            def f(t, y, ydot):
                precip = self.rainfall_data_dict.get(math.ceil(t), 0)
                evap = self.evap_data_dict.get(math.ceil(t), 0)
                d = pystreamflow.ode.ode_rhs(
                    t,
                    *y[:-1],
                    precip,
                    evap,
                    *parameters,
                    alpha_s,
                    alpha_i)

                ydot[0] = d[0]
                ydot[1] = d[1]
                ydot[2] = d[2]
                ydot[3] = d[3]
                ydot[4] = d[4]

            t_eval = list(np.arange(0, times[0])) + list(times)
            solution = scikits.odes.ode(
                'cvode',
                f,
                old_api=False,
                rtol=self.rtol,
                atol=self.atol)

            solution = solution.solve(t_eval, self.init_cond)

            y = solution.values.y[-len(times)-1:, 4]

        # Take the difference, which corresponds to the measurements (flow)
        y = np.diff(y)

        if len(y) != len(times):
            # At bad parameter values, CVODE can fail and return a short y
            return [np.nan] * len(times)

        return y
