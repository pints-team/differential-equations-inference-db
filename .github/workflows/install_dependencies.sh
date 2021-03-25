#!/bin/bash

# Update apt-get
apt-get -qq update;

# Install Sundials (for CVODE)
apt-get install libopenblas-dev liblapack-dev
apt-get install -y libsundials-dev;
