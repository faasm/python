FROM faasm/cpp-sysroot:0.0.16

RUN apt install -y \
    libssl-dev \
    ninja-build

WORKDIR /code/faasm-cpython
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Install build Python (careful with Docker cache here)
WORKDIR /code/faasm-cpython
COPY bin/install_build_python.sh bin/install_build_python.sh
RUN ./bin/install_build_python.sh

# Add the rest of the code
COPY . .

# Install pyfaasm natively
WORKDIR /code/faasm-cpython/pyfaasm
RUN pip3 install .

# Build CPython
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
