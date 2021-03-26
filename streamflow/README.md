# pystreamflow

pystreamflow enables efficient simulation and inference for rainfall runoff differential equation models of the sort that arise in hydrological modelling of river basins.

## Installation

1. Navigate to `differential-equations-inference-db/streamflow/` (this directory)
1. For a simple install, run `pip install .`
1. To install with support for the CVODE solver via scikits.odes, run `pip install .[cvode]`

### Installing with CVODE

The CVODE solver enables faster model evaluations and inference, but it requires you to install the SUNDIALS C library and the scikits.odes Python package. The following is a typical install process for the 5.1.0 version of SUNDIALS:

```
sudo apt-get install libopenblas-dev liblapack-dev
wget https://github.com/LLNL/sundials/releases/download/v5.1.0/sundials-5.1.0.tar.gz
tar xzf sundials-5.1.0.tar.gz
mkdir build-sundials-5.1.0
cd build-sundials-5.1.0/
cmake -DLAPACK_ENABLE=ON -DSUNDIALS_INDEX_SIZE=64 ../sundials-5.1.0/
make install
```

scikits.odes is pip installable, but it is often necessary to refer to its [installation documentation](https://scikits-odes.readthedocs.io/en/latest/installation.html), which contains troubleshooting information.

If you have conda, an alternative is to use conda forge:

```
conda install -c conda-forge scikits.odes
```

## Usage

Once installed, the streamflow model can be accessed using the `pystreamflow.RiverModel` class and the data can be accessed using the `pystreamflow.load_data` function. The raw data files are available [here](pystreamflow/data/), and the model code is [here](pystreamflow/model.py).

Refer to the notebook in the examples directory for typical usage.
