FROM faasm/sysroot:0.0.10
ARG FAASM_CPYTHON_VERSION

RUN apt install -y \
    libssl-dev \
    ninja-build

# Install build Python separately here to avoid invalidating the cache
# unnecessarily 
COPY bin/install_build_python.sh bin/install_build_python.sh
RUN ./bin/install_build_python.sh

# Check out the latest code
WORKDIR /code
RUN git clone -b v${FAASM_CPYTHON_VERSION} https://github.com/faasm/faasm-cpython

# Set up submodules
WORKDIR /code/faasm-cpython
RUN git submodule update --init

# Install Python requirements
RUN pip3 install -r requirements.txt

# Build CPython
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
