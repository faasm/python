#!/bin/bash

# Activate the crossenv *before* adding any extra environment vars
. ./cross_venv/bin/activate

# Make wasm toolchain variables available
TOOLCHAIN_ROOT=/usr/local/code/faasm/third-party/faasm-toolchain
source ${TOOLCHAIN_ROOT}/env.sh

# The following variables aren't picked up by the CPython build
# Note: although we're building static libraries, certain modules will still
# pick up LDSHARED
export LDSHARED="${WASM_LDSHARED} -L ${WASM_LIBRARY_PATH}"

