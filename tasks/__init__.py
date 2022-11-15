from invoke import Collection

from . import (
    cpython,
    docker,
    func,
    git,
    libs,
    mxnet,
    runtime,
)

ns = Collection(
    cpython,
    docker,
    func,
    git,
    libs,
    mxnet,
    runtime,
)
