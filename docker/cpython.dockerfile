FROM faasm/sysroot:v0.0.7

RUN apt install -y \
    libssl-dev \
    ninja-build

WORKDIR /code/faasm-cpython
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Install build Python (careful with Docker cache here)
COPY bin/install_build_python.sh bin/install_build_python.sh
RUN ./bin/install_build_python.sh

# Add the rest of the code
COPY . .

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
