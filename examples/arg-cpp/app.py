# pylint: disable=missing-module-docstring

from sushipy.main import Sushi

if __name__ == "__main__":
    Sushi()

    # after first launch, we can call function from c++
    from out.main import helloWorld

    helloWorld(1)
