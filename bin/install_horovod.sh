#!/bin/bash

set -e

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PROJ_ROOT=${THIS_DIR}/..
HOROVOD_DIR=${PROJ_ROOT}/third-party/horovod

# Start the cross-env
pushd ${HOROVOD_DIR} >> /dev/null
HOROVOD_WITH_MXNET=1 pip install .
popd >> /dev/null

