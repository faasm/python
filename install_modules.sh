#!/bin/bash

set -e

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Start the cross-env
source cross_venv/bin/activate

# Numpy (parallel build https://numpy.org/devdocs/user/building.html)
export NPY_NUM_BUILD_JOBS=$(nproc --ignore 1)
echo "Numpy using ${NPY_NUM_BUILD_JOBS} cores"
pushd ${THIS_DIR}/third-party/numpy >> /dev/null
pip install .
popd >> /dev/null

# Pyfaasm
pushd ${THIS_DIR}/third-party/pyfaasm >> /dev/null
pip install .
popd >> /dev/null

