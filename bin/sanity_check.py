import sysconfig
from pprint import pprint
from os import environ


def main():
    # Sysconfig checks
    print("Platform: {}".format(sysconfig.get_platform()))
    print("Python version: {}".format(sysconfig.get_python_version()))
    print(
        "Current installation scheme: {}".format(
            sysconfig._get_default_scheme()
        )
    )
    print("Paths")
    pprint(sysconfig.get_paths())
    print("Variables")
    pprint(sysconfig.get_config_vars())

    print("Environment")
    environ_dict = {k: v for k, v in environ.items()}
    pprint(environ_dict)


if __name__ == "__main__":
    main()
