FROM faasm/sysroot:0.0.7

RUN apt install -y \
    libssl-dev

WORKDIR cpython
COPY requirements.txt .
RUN pip3 install -r requirements.txt


COPY . .

# Install build Python
RUN ./bin/install_build_python.sh

# Install crossenv
RUN ./bin/crossenv_setup.sh

# Build mxnet
RUN inv mxnet

# Build cpython
RUN inv cpython

# Cross-compile packages
RUN . ./cross_venv/bin/activate && inv libs.install
RUN . ./cross_venv/bin/activate && inv libs.install --experimental
