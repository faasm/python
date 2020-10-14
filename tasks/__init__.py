from invoke import Collection

from . import (
    container,
    cpython,
    git,
    libs,
    mxnet,
    runtime,
)

ns = Collection(
    container,
    cpython,
    git,
    libs,
    mxnet,
    runtime,
)
