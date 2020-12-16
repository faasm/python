FROM faasm/cpp-sysroot:0.0.16
ARG FAASM_CPYTHON_VERSION

RUN apt install -y \
    libssl-dev \
    ninja-build

# Hack to avoid rebuilding build CPython every time the code changes
WORKDIR /tmp
COPY bin/install_build_python.sh .
RUN ./install_build_python.sh

# Clone current tag
WORKDIR /code
RUN git clone \
    -b v${FAASM_CPYTHON_VERSION} \
    https://github.com/faasm/faasm-cpython

# Submodules
WORKDIR /code/faasm-cpython
RUN git submodule update --init

# Install pyfaasm natively
RUN inv pyfaasm.native

# Build CPython to wasm
RUN inv cpython

# Set up crossenv
RUN ./bin/crossenv_setup.sh

# Install cross-compiled python packages
RUN . ./cross_venv/bin/activate && inv libs.install

# TODO - enable these once the MXNet/ Horovod work is completed
# Build mxnet
# RUN inv mxnet

# Install experimental pacakges
# RUN . ./cross_venv/bin/activate && inv libs.install --experimental

# Copy files into place
RUN inv runtime
