from faasmtools.docker import (
    ACR_NAME,
    build_container,
    push_container,
)
from invoke import task
from os.path import join
from tasks.env import (
    PROJ_ROOT,
    get_version,
)

CONTAINER_IMAGE = "{}/cpython".format(ACR_NAME)
DOCKERFILE = join(PROJ_ROOT, "Dockerfile")


def _get_tag():
    tag_name = "{}:{}".format(CONTAINER_IMAGE, get_version())
    return tag_name


@task(default=True)
def build(ctx, nocache=False, push=False):
    """
    Build current version of the cpython container
    """
    build_container(
        _get_tag(),
        DOCKERFILE,
        PROJ_ROOT,
        nocache=nocache,
        push=push,
        build_args={"FAASM_PYTHON_VERSION": get_version()},
    )


@task
def push(ctx):
    """
    Push the current version of the cpython container
    """
    push_container(_get_tag())
