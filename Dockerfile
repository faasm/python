FROM faasm/cpp-sysroot:0.0.16
ARG FAASM_CPYTHON_VERSION

RUN apt install -y \
    libssl-dev \
    ninja-build

# Clone current tag
WORKDIR /code
RUN git clone \
    -b v${FAASM_CPYTHON_VERSION} \
    https://github.com/faasm/faasm-cpython

# Install the build machine CPython
WORKDIR /code/faasm-cpython
RUN ./bin/install_build_python.sh

# Install pyfaasm natively
WORKDIR /code/faasm-cpython/pyfaasm
RUN pip3 install .

# Build CPython to wasm
WORKDIR /code/faasm-cpython
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
