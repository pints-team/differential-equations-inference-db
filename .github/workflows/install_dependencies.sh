#!/bin/bash

# Update apt-get
apt-get -qq update;

# Install Sundials (for CVODE)
apt-get install -y libsundials-dev;
