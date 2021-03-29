************
pystreamflow
************

The pystreamflow model can be used to study river discharge data.

This package provides a PINTS Forward Model for simulation and inference, and a
function for loading precipitation, evaporation, and discharge data in Pandas
format.

.. currentmodule:: pystreamflow

Forward model
*************

.. autoclass:: pystreamflow.RiverModel
  :members: __init__, simulate, set_model_data

Data
****

.. autofunction:: pystreamflow.load_data
