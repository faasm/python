#!/bin/bash

set -e

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# NOTE - all the commands must use the specially-installed python 
# on the build machine.
BUILD_PYTHON_BIN=/usr/local/faasm/python3.8/bin
BUILD_PYTHON=${BUILD_PYTHON_BIN}/python3.8
BUILD_PIP=${BUILD_PYTHON_BIN}/pip3.8

# Install the crossenv module in dev mode
CROSSENV_SRC_DIR=${THIS_DIR}/third-party/crossenv
echo "Installing crossenv from ${CROSSENV_SRC_DIR}"
pushd ${CROSSENV_SRC_DIR} >> /dev/null
${BUILD_PIP} install -e .
popd >> /dev/null

# Run the set-up script
pushd ${THIS_DIR} >> /dev/null
${BUILD_PYTHON} crossenv_setup.py
popd >> /dev/null