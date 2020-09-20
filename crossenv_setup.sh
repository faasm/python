#!/bin/bash

set -e

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# NOTE - all the commands must use the specially-installed python 
# on the build machine.
BUILD_PYTHON_BIN=/usr/local/faasm/python3.8/bin
BUILD_PYTHON=${BUILD_PYTHON_BIN}/python3.8
BUILD_PIP=${BUILD_PYTHON_BIN}/pip3.8

# Install the build machine python dependencies
CROSSENV_SRC_DIR=${THIS_DIR}/third-party/crossenv
echo "Installing crossenv from ${CROSSENV_SRC_DIR}"
pushd ${CROSSENV_SRC_DIR} >> /dev/null
${BUILD_PIP} install -e .

echo "Installing cython"
${BUILD_PIP} install cython
popd >> /dev/null

pushd ${THIS_DIR} >> /dev/null

# Run the set-up script
${BUILD_PYTHON} crossenv_setup.py

# Enter the env and print details
source cross_venv/bin/activate
echo ""
echo "Inside crossenv: "
echo "pip3.8 is:    $(which pip3.8)"
echo "python3.8 is: $(which python3.8)"

popd >> /dev/null


