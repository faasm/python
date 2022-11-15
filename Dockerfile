FROM faasm/cpp-sysroot:0.2.0
ARG FAASM_PYTHON_VERSION

SHELL ["/bin/bash", "-c"]
ENV PYTHON_DOCKER="on"

RUN apt update && apt install -y libssl-dev

# Clone code and submodules
RUN mkdir -p /code \
    && git clone \
        -b v${FAASM_PYTHON_VERSION} \
        https://github.com/faasm/python \
        /code/python \
    && git submodule update --init

# Hack to avoid rebuilding build CPython every time the code changes
# COPY bin/install_build_python.sh /tmp/
# RUN cd /tmp \
    #     && ./install_build_python.sh
#
# # Cross-compile CPython to WASM
# # TODO: use venvs
# RUN cd /code/python \
    #     && pip3 install -r requirements.txt \
    #     && inv cpython
#
# # Set up crossenv to cross-compile python libraries to WASM
# RUN cd /code/python \
    #     && ./bin/crossenv_setup.sh \
    #     && inv \
    #         func \
    #         runtime

# Install cross-compiled python packages
# RUN . ./cross_venv/bin/activate && inv libs.install

# Build Faasm function
# RUN inv func

# Copy files into place
# RUN inv runtime

# TODO - enable these once the MXNet/ Horovod work is completed
# Build mxnet
# RUN inv mxnet

# Install experimental pacakges
# RUN . ./cross_venv/bin/activate && inv libs.install --experimental

