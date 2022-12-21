from invoke import Collection

from . import (
    cpython,
    docker,
    format_code,
    func,
    git,
    modules,
    mxnet,
)

ns = Collection(
    cpython,
    docker,
    format_code,
    func,
    git,
    modules,
    mxnet,
)
