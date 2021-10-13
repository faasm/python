from invoke import Collection

from . import (
    container,
    cpython,
    func,
    git,
    libs,
    mxnet,
    runtime,
)

ns = Collection(
    container,
    cpython,
    func,
    git,
    libs,
    mxnet,
    runtime,
)
