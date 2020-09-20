#!/bin/bash

set -e

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# NOTE - all the commands must use the specially-installed python 
# on the build machine.

BUILD_PYTHON_BIN=/usr/local/faasm/python3.8/bin
BUILD_PYTHON=${BUILD_PYTHON_BIN}/python3.8
BUILD_PIP=${BUILD_PYTHON_BIN}/pip3.8

WASM_SYSROOT=/usr/local/faasm/llvm-sysroot
WASM_CPYTHON=${THIS_DIR}/third-party/cpython/install/wasm/bin/python3.8

CROSSENV_VENV_DIR=${THIS_DIR}/cross_venv
CROSSENV_SRC_DIR=${THIS_DIR}/third-party/crossenv

# Clean existing crossenv virtual environment
if [ -d "$CROSSENV_VENV_DIR" ]; then
    rm -r ${CROSSENV_VENV_DIR}
fi

# Install the crossenv module in dev mode
pushd ${CROSSENV_SRC_DIR} >> /dev/null
${BUILD_PIP} install -e .
popd >> /dev/null

# Set up crossenv
${BUILD_PYTHON} -m crossenv \
    ${WASM_CPYTHON} \
    ${CROSSENV_VENV_DIR} \
    -vvv \
    --sysroot=${WASM_SYSROOT}

