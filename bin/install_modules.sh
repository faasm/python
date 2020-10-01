#!/bin/bash

set -e

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PROJ_ROOT=${THIS_DIR}/..

# Start the cross-env
pushd ${PROJ_ROOT} >> /dev/null
source cross_venv/bin/activate
popd >> /dev/null

# Numpy (parallel build https://numpy.org/devdocs/user/building.html)
export NPY_NUM_BUILD_JOBS=$(nproc --ignore 1)
echo "Numpy using ${NPY_NUM_BUILD_JOBS} cores"
pushd ${PROJ_ROOT}/third-party/numpy >> /dev/null
# pip install .
popd >> /dev/null

# Pyfaasm
pushd ${PROJ_ROOT}/third-party/pyfaasm >> /dev/null
pip install .
popd >> /dev/null

# Other modules (can be installed unmodified)
pip install dulwich
pip install Genshi
pip install pyaes
pip install pyperf
pip install pyperformance
pip install six

# Torch errors on a module import
# pip install torch

