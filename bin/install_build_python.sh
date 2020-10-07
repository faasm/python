#!/bin/bash

set -e

PYTHON_VER=Python-3.8.2
TAR_NAME=${PYTHON_VER}.tgz
TAR_URL=https://www.python.org/ftp/python/3.8.2/${TAR_NAME}

INSTALL_PREFIX=/usr/local/faasm/python3.8
PYTHON_BIN=${INSTALL_PREFIX}/bin/python3.8
PIP_BIN=${INSTALL_PREFIX}/bin/pip3.8

N_PROC=$(nproc --ignore 1)

pushd /tmp/ >> /dev/null

# Download the TAR file and extract
wget ${TAR_URL}
tar -xf ${TAR_NAME}

# Configure and install
pushd ${PYTHON_VER} >> /dev/null
./configure --prefix=${INSTALL_PREFIX}
make -j ${N_PROC} altinstall
popd >> /dev/null

# Update pip
${PIP_BIN} install -U pip

# Print version
${PYTHON_BIN} --version

popd >> /dev/null


