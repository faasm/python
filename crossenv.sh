#!/bin/bash

# First activate the crossenv
. ./cross_venv/bin/activate

# Set up environment variables
TOOLCHAIN_ROOT=/usr/local/code/faasm/third-party/faasm-toolchain
source ${TOOLCHAIN_ROOT}/env.sh

# Make sure tools are set properly
#export CC=${WASM_CC}
#export AR=${WASM_AR}
#export CXX=${WASM_CXX}
# export CFLAGS=${WASM_CFLAGS}
# export CXXFLAGS=${WASM_CXXFLAGS}
#export CPP=${WASM_CPP}
#export RANLIB=${WASM_RANLIB}
#export LD=${WASM_LD}

# For some reason these aren't picked up as part of the CPython build
export LDSHARED="${WASM_LD} --no-entry"
export LDCXXSHARED="${WASM_LD} --no-entry"
