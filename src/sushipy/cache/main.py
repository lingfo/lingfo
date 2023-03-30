"""
cache
"""

# pylint: disable=no-method-argument, too-few-public-methods

import fileinput
import importlib
from os import name, path
from shutil import copyfile

DIR_SLASH = "\\" if name == "nt" else "/"


class Cache:
    """cache"""

    def _exists(self) -> bool:
        return path.isfile("sushicache.py")

    # TODO: make it so when updating cache we dont need to provide
    # old data (Cache.update('CUSTOM_TEMP_FILE = None', 'CUSTOM_TEMP_FILE = '))
    def update(self, old: str, new: str):
        """
        overwrites old cache data with new one
        """

        with fileinput.input("sushicache.py", inplace=True) as f:
            for line in f:
                new_line = line.replace(old, new)
                print(new_line, end="")

    def _copy_template(self) -> None:
        lib_path = importlib.util.find_spec("sushipy").origin
        lib_path = lib_path.replace(
            "__init__.py", f"{DIR_SLASH}cache{DIR_SLASH}cache_template.py"
        )

        copyfile(lib_path, "sushicache.py")

    def __init__(self) -> None:
        # if cache doesnt exists, create one
        if not self._exists():
            self._copy_template()
