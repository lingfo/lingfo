# pylint: disable=missing-module-docstring
from sushipy.main import Sushi

if __name__ == "__main__":
    Sushi()

    # sushi generates code for us to call in Python
    from out.main import array_sum

    array_sum()
