# pylint: disable=missing-module-docstring

from lingfopy.main import Lingfo

if __name__ == "__main__":
    Lingfo()

    # after first launch, we can call function from c++
    from out.main import helloWorld

    helloWorld()
