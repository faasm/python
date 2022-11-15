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
    && cd /code/python \
    && git submodule update --init -f third-party/cpp \
    && git submodule update --init -f third-party/cpython \
    && git submodule update --init -f third-party/crossenv \
    && ./bin/install_build_python.sh

# Cross-compile CPython to WASM and the python libraries
RUN cd /code/python \
    && ./bin/create_venv.sh \
    && source ./venv/bin/activate \
    && inv \
        cpython \
    && ./bin/crossenv_setup.sh \
    && source ./venv/bin/activate \
    && inv \
        func \
        runtime

# Install cross-compiled python packages
RUN cd /code/python \
    && source ./cross_venv/bin/activate \
    && pip3 install -r crossenv/requirements.txt \
    && inv -r crossenv libs.install


# TODO: enable these once the MXNet/ Horovod work is completed
# Build mxnet
# RUN inv mxnet

# TODO: Install experimental pacakges
# RUN . ./cross_venv/bin/activate && inv libs.install --experimental

WORKDIR /code/python
ENV TERM xterm-256color
RUN sed -i 's/\/code\/cpp\/bin/\/code\/python\/bin/g' ~/.bashrc
CMD ["/bin/bash", "-l"]
