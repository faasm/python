#!/bin/bash

# ----------------------------
# Container-specific settings
# ----------------------------

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]:-${(%):-%x}}" )" >/dev/null 2>&1 && pwd )"
PROJ_ROOT="${THIS_DIR}/.."
MODE="undetected"
if [[ -z "$PYTHON_DOCKER" ]]; then
    # Normal terminal
    VENV_PATH="${PROJ_ROOT}/venv-bm"
    MODE="terminal"
else
    VENV_PATH="${PROJ_ROOT}/venv"
    # Use containerised redis
    alias redis-cli="redis-cli -h redis"
    MODE="container"
fi

pushd ${PROJ_ROOT}>>/dev/null

# ----------------------------
# Virtualenv
# ----------------------------

if [ ! -d ${VENV_PATH} ]; then
    ./bin/create_venv.sh
fi

export VIRTUAL_ENV_DISABLE_PROMPT=1
source ${VENV_PATH}/bin/activate

# ----------------------------
# Environment vars
# ----------------------------

VERSION_FILE=${PROJ_ROOT}/VERSION
export PYTHON_ROOT=${PROJ_ROOT}
export PYTHON_VERSION=$(cat ${VERSION_FILE})

export PS1="(python) $PS1"

# -----------------------------
# Splash
# -----------------------------

echo ""
echo "----------------------------------"
echo "Python CLI"
echo "Version: ${PYTHON_VERSION}"
echo "Project root: ${PYTHON_ROOT}"
echo "Mode: ${MODE}"
echo "----------------------------------"
echo ""

popd >> /dev/null
