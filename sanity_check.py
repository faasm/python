import distutils.ccompiler
import sysconfig
from pprint import pprint


def main():
    # Sysconfig checks
    print("Platform: {}".format(sysconfig.get_platform()))
    print("Python version: {}".format(sysconfig.get_python_version()))
    print("Current installation scheme: {}".format(
        sysconfig._get_default_scheme()))
    print("Paths")
    pprint(sysconfig.get_paths())
    print("Variables")
    pprint(sysconfig.get_config_vars())

    # Distutils checks
    print("Compiler: {}".format(distutils.ccompiler.get_default_compiler()))


if __name__ == "__main__":
    main()
