from faasmtools.git import tag_project
from invoke import task
from subprocess import run
from tasks.env import PROJ_ROOT, get_version

VERSIONED_FILES = [
    ".github/workflows/tests.yml",
    "VERSION",
]


def get_tag_name(version):
    return "v{}".format(version)


@task
def bump(ctx, ver=None):
    """
    Bump code version
    """
    old_ver = get_version()

    if ver:
        new_ver = ver
    else:
        # Just bump the last minor version part
        new_ver_parts = old_ver.split(".")
        new_ver_minor = int(new_ver_parts[-1]) + 1
        new_ver_parts[-1] = str(new_ver_minor)
        new_ver = ".".join(new_ver_parts)

    # Replace version in all files
    for f in VERSIONED_FILES:
        sed_cmd = "sed -i 's/{}/{}/g' {}".format(old_ver, new_ver, f)
        run(sed_cmd, shell=True, check=True)


@task
def tag(ctx, force=False):
    """
    Creates git tag from the current tree
    """
    version = get_version()
    tag_name = "v{}".format(version)
    tag_project(tag_name, PROJ_ROOT, force=force)
