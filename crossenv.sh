#!/bin/bash

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# NOTE - all the commands must use the specially-installed python 
# on the build machine.

BUILD_PYTHON_BIN=/usr/local/faasm/python3.8/bin
BUILD_PYTHON=${PYTHON_BIN}/python3.8
BUILD_PIP=${PYTHON_BIN}/pip3.8

WASM_SYSROOT=/usr/local/faasm/llvm-sysroot
WASM_CPYTHON=${WASM_SYSROOT}/bin/python3.8

CROSSENV_DIR=${THIS_DIR}

# Clean existing directory
if [ -d "$CROSSENV_DIR" ]; then
    rm -r ${CROSSENV_DIR}
fi

# Install the crossenv module
${BUILD_PIP} install crossenv

# Set up crossenv
${BUILD_PYTHON} -m crossenv \
    ${WASM_CPYTHON} \
    cross_venv \
    -vvv \
    --sysroot=${WASM_CPYTHON}

