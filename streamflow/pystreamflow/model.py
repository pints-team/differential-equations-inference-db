"""PINTS implementation of the rainfall runoff model.
"""

import math


def flux(S, a):
    r"""Flux function for hydrological processes.

    This is a general function for the relative flux as it depends on relative
    storage and a single shape parameter.

    The equation is given by

    .. math::
        f(S, a) = \frac{1 - e^{-aS}}{1 - e^{-a}}

    To prevent overflow, values of -a*S or -a which exceed 600 will be
    truncated to 600. This limit should not be reached with typical values of a
    and S, but it helps to protect the function during inference if strange
    values are provided by some algorithm. Confer
    https://github.com/Zaijab/DREAM/blob/master/examples/example_14/crr_model.c

    Parameters
    ----------
    S : float
        Relative storage
    a : float
        Shape parameter

    Returns
    -------
    float
        Flux
    """
    if abs(a) <= 1e-6:
        # For zero or near-zero a, the flux is linear or near-linear. Use the
        # linear approximation, as the flux function is unstable at these
        # values.
        return S

    return (1 - math.exp(min(600, -a * S))) / (1 - math.exp(min(600, -a)))
