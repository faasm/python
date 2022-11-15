from invoke import Collection

from . import (
    cpython,
    docker,
    format_code,
    func,
    git,
    libs,
    mxnet,
    runtime,
)

ns = Collection(
    cpython,
    docker,
    format_code,
    func,
    git,
    libs,
    mxnet,
    runtime,
)
