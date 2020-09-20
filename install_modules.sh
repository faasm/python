#!/bin/bash

set -e

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Start the cross-env
source cross_venv/bin/activate

# Numpy
pushd ${THIS_DIR}/third-party/numpy >> /dev/null
pip install .
popd >> /dev/null

# Pyfaasm
pushd ${THIS_DIR}/third-party/pyfaasm >> /dev/null
pip install .
popd >> /dev/null

