FROM faasm.azurecr.io/cpp-sysroot:0.2.4
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
    && git config --global --add safe.directory /code/python

# Cross-compile CPython to WASM and the python libraries
RUN cd /code/python \
    && ./bin/create_venv.sh \
    && source ./venv/bin/activate \
    # Buld and install a native CPython and a cross-compiled CPython with the
    # same version. Also cross-compile the entrypoint function for CPython
    && inv \
        cpython.native \
        cpython.wasm \
        cpython.func

# Build cross-compiled python modules, including `pyfaasm`
RUN cd /code/python \
    && ./bin/crossenv_setup.sh \
    && source ./cross_venv/bin/activate \
    && pip3 install -r crossenv/requirements.txt \
    && inv -r crossenv modules.build

# Finally, install the cross-compiled Python modules
RUN cd /code/python \
    && source ./venv/bin/activate \
    && inv modules.install


# TODO: enable these once the MXNet/ Horovod work is completed
# Build mxnet
# RUN inv mxnet

# TODO: Install experimental pacakges
# RUN . ./cross_venv/bin/activate && inv libs.install --experimental

WORKDIR /code/python
ENV TERM xterm-256color
RUN sed -i 's/\/code\/cpp\/bin/\/code\/python\/bin/g' ~/.bashrc
CMD ["/bin/bash", "-l"]
