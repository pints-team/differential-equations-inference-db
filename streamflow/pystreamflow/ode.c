#include <Python.h>
#define _USE_MATH_DEFINES
#include <math.h>
#include <float.h>


// Flux function
static double
flux_calc(double s, double a) {
  double f;

  // Values of s above 1 or below 0 are reset to the most extreme plausible
  // value
  if (s > 1.0)
    s = 1.0;
  if (s < 0.0)
    s = 0.0;

  // For zero or near-zero a, the flux is linear or near-linear. Use the
  // linear approximation, as the flux function is unstable at these
  // values.
  if (abs(a) <= 0.00001)
    return s;

  f = (1 - exp(fmin(600.0, -a * s))) / (1 - exp(fmin(600.0, -a)));
  return f;
}


// Flux function in Python
static const char flux_docstring[] = \
"Flux function for hydrological processes.\n"
"\n"
"This is a general function for the relative flux as it depends on relative\n"
"storage and a single shape parameter.\n"
"\n"
"The equation is given by\n"
"\n"
".. math::\n"
"    f(S, a) = \\frac{1 - e^{-aS}}{1 - e^{-a}}\n"
"\n"
"To prevent overflow, values of -a*S or -a which exceed 600 will be\n"
"truncated to 600. This limit should not be reached with typical values of a\n"
"and S, but it helps to protect the function during inference if strange\n"
"values are provided by some algorithm. Confer\n"
"https://github.com/Zaijab/DREAM/blob/master/examples/example_14/crr_model.c\n"
"\n"
"Parameters\n"
"----------\n"
"S : float\n"
"    Relative storage\n"
"a : float\n"
"    Shape parameter\n"
"\n"
"Returns\n"
"-------\n"
"float\n"
"    Flux\n";
static PyObject *
flux(PyObject *self, PyObject *args) {
  double s;
  double a;

  // read arguments from python
  if (!PyArg_ParseTuple(args, "dd", &s, &a))
    return NULL;

  return PyFloat_FromDouble(flux_calc(s, a));
}


// ODE function in Python
static const char ode_rhs_docstring[] = \
"Evaluate the differential equations.\n"
"\n"
"Parameters\n"
"----------\n"
"t : float\n"
"    Time\n"
"y : list\n"
"    Current values for [S_i, S_u, S_s, S_f, z]\n"
"precip : float\n"
"    Precipitation at this day\n"
"evap : float\n"
"    Evaporation at this day\n"
"I_max : float\n"
"    maximum interception parameter\n"
"S_umax : float\n"
"    unsaturated storage capacity parameter\n"
"Q_smax : float\n"
"    maximum percolation parameter\n"
"alpha_e : float\n"
"    evaporation flux shape parameter\n"
"alpha_f : float\n"
"    runoff flux shape parameter\n"
"K_s : float\n"
"    slow reservoir time constant parameter\n"
"K_f : float\n"
"    fast reservoir time constant parameter\n"
"alpha_s : float\n"
"    percolation flux shape parameter\n"
"alpha_i : float\n"
"    interception flux shape parameter\n"
"\n"
"Returns\n"
"-------\n"
"list\n"
"    Derivatives for [S_i, S_u, S_s, S_f, z]\n";
static PyObject *
ode_rhs(PyObject *self, PyObject *args) {

  // variables and model data
  double t;
  double S_i;
  double S_u;
  double S_s;
  double S_f;
  double precip;
  double evap;

  // model parameters
  double I_max;
  double S_umax;
  double Q_smax;
  double alpha_e;
  double alpha_f;
  double k_s;
  double k_f;
  double alpha_s;
  double alpha_i;

  // read arguments from python
  if (!PyArg_ParseTuple(args, "dddddddddddddddd", &t, &S_i, &S_u, &S_s, &S_f,
      &precip, &evap, &I_max, &S_umax, &Q_smax, &alpha_e, &alpha_f, &k_s, &k_f,
      &alpha_s, &alpha_i))
    return NULL;

  // temporary variables for calculation of ode function
  double intercept_evap;
  double effect_precip;
  double unsat_evap;
  double percolation;
  double runoff;
  double slow_stream;
  double fast_stream;

  // Interception component
  intercept_evap = evap * flux_calc(S_i / I_max, alpha_i);
  effect_precip = precip * flux_calc(S_i / I_max, -alpha_i);

  // Unsaturated storage
  unsat_evap = fmax(0.0, evap - intercept_evap) * flux_calc(S_u / S_umax, alpha_e);

  // Percolation and runoff
  percolation = Q_smax * flux_calc(S_u / S_umax, alpha_s);
  runoff = effect_precip * flux_calc(S_u / S_umax, alpha_f);

  // Reservoirs
  slow_stream = S_s / k_s;
  fast_stream = S_f / k_f;

  // Calculate derivatives
  double d1;
  double d2;
  double d3;
  double d4;
  double d5;

  d1 = precip - intercept_evap - effect_precip;
  d2 = effect_precip - unsat_evap - percolation - runoff;
  d3 = percolation - slow_stream;
  d4 = runoff - fast_stream;
  d5 = slow_stream + fast_stream;

  // Return as a python list of floats
  return Py_BuildValue("[fffff]", d1, d2, d3, d4, d5);
}


// Methods table for python
static PyMethodDef OdeMethods[] = {
  {"ode_rhs", ode_rhs, METH_VARARGS, ode_rhs_docstring},
  {"flux", flux, METH_VARARGS, flux_docstring},
  {NULL, NULL, 0, NULL} /* Sentinel */
};


// Python module
static struct PyModuleDef ode = {
  PyModuleDef_HEAD_INIT,
  "ode",
  NULL,
  -1,
  OdeMethods
};


PyMODINIT_FUNC
PyInit_ode(void){
  return PyModule_Create(&ode);
}


// From https://docs.python.org/3/extending/extending.html
int
main(int argc, char *argv[]) {
  wchar_t *program = Py_DecodeLocale(argv[0], NULL);
  if (program == NULL) {
      fprintf(stderr, "Fatal error: cannot decode argv[0]\n");
      exit(1);
  }

  /* Add a built-in module, before Py_Initialize */
  PyImport_AppendInittab("ode", PyInit_ode);

  /* Pass argv[0] to the Python interpreter */
  Py_SetProgramName(program);

  /* Initialize the Python interpreter.  Required. */
  Py_Initialize();

  /* Optionally import the module; alternatively,
     import can be deferred until the embedded script
     imports it. */
  PyImport_ImportModule("ode");

  PyMem_RawFree(program);
  return 0;
}
