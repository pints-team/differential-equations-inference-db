# bayesian-differential-equations-db

The purpose of bayesian-differential-equations-db is to provide a database of differential equation models and associated observed time series data that represent interesting and challenging problems for inference. The database provides methods for running these models and accessing the associated observed data files using Python.

While the [`pints.toy`](https://pints.readthedocs.io/en/latest/toy/index.html) module already includes a number of simple models and distributions, this repository is intended for more complex models associated with real experimental data.

## Models and data

| Model | Reference | Features |
| ----- | --------- | -------- |
| [Rainfall-runoff river discharge data, French Broad River at Asheville, NC.](streamflow/) | [[1]](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2009WR008933) | Complex noise noise process, potential model misspecification, importance of numerical accuracy |
