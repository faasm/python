#!/bin/bash

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Toolchain
TOOLCHAIN_ROOT=/usr/local/code/faasm/toolchain
TOOLCHAIN_BIN=${TOOLCHAIN_ROOT}/install/bin

source ${TOOLCHAIN_ROOT}/env.sh
export PATH=${TOOLCHAIN_BIN}:${PATH}

# Toolchain env vars
CC=${WASM_CC}
AR=${WASM_AR}
CXX=${WASM_CXX}
CFLAGS=${WASM_CFLAGS}
CXXFLAGS=${WASM_CXXFLAGS}
CPP=${WASM_CPP}
RANLIB=${WASM_RANLIB}
LD=${WASM_LD}

# Force the use of the right build python
PYTHON_BIN_DIR=/usr/local/faasm/python3.8/bin
export PATH=${PYTHON_BIN_DIR}:${PATH}

PYTHON=${PYTHON_BIN_DIR}/python3.8
PIP=${PYTHON_BIN_DIR}/pip3.8
HOST_PYTHON=${THIS_DIR}/third-party/cpython/install/wasm

# Set up the cross-compile environment
if [ ! -d "cross_venv" ]; then
    ${PIP} install crossenv
    ${PYTHON} -m crossenv ${HOST_PYTHON} cross_venv
fi

export VIRTUAL_ENV_DISABLE_PROMPT=1
. ./cross_venv/bin/activate
pip install -U pip
pip install -r requirements.txt

export PS1="(pyodide) $PS1"

