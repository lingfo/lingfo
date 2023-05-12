# pylint: disable=missing-module-docstring, unused-import
import timeit

from lingfo.main import Lingfo

if __name__ == "__main__":
    Lingfo()

    # lingfo generates code for us to call in Python
    from out.main import itt_add, double_number

    # Time the itt_add() function
    itt_add_time = timeit.timeit(
        "itt_add()", setup="from __main__ import itt_add", number=1
    )
    # Print the results
    print("itt_add() took", itt_add_time, "seconds")

    # Run a function with arguments
    double_number(5)
