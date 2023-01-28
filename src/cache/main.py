"""
cache
"""

# pylint: disable=no-method-argument, too-few-public-methods

import fileinput
from os import path
from shutil import copyfile


class Cache:
    """cache"""

    def _exists(self) -> bool:
        return path.isfile("sushicache.py")

    def update(self, old: str, new: str):
        """
        overwrites old cache data with new one
        """

        with fileinput.input("sushicache.py", inplace=True) as f:
            for line in f:
                new_line = line.replace(old, new)
                print(new_line, end="")

    def _copy_template(self) -> None:
        copyfile("src/cache/cache_template", "sushicache.py")

    def __init__(self) -> None:
        # if cache doesnt exists, create one
        if not self._exists():
            self._copy_template()
