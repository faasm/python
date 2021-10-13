from pyperformance.benchmarks.bm_deltablue import delta_blue


def faasm_main():
    print("Running deltablue python benchmark")

    delta_blue(100)

    print("Deltablue python benchmark complete")

    return 0
