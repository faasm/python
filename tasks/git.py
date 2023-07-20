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
def bump(ctx, patch=False, minor=False, major=False):
    """
    Bump the code version by --patch, --minor, or --major
    """
    old_ver = get_version()
    new_ver_parts = old_ver.split(".")

    if patch:
        idx = 2
    elif minor:
        idx = 1
    elif major:
        idx = 0
    else:
        raise RuntimeError("Must set one in: --[patch,minor,major]")

    # Change the corresponding idx
    new_ver_parts[idx] = str(int(new_ver_parts[idx]) + 1)

    # Zero-out the following version numbers (i.e. lower priority). This is
    # because if we tag a new major release, we want to zero-out the minor
    # and patch versions (e.g. 0.2.0 comes after 0.1.9)
    for next_idx in range(idx + 1, 3):
        new_ver_parts[next_idx] = "0"

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
