"""
cache
"""

# pylint: disable=no-method-argument, too-few-public-methods

from os import path
from shutil import copyfile


class Cache:
    """cache"""

    def _exists(self) -> bool:
        return path.isfile("sushicache.py")

    def _copy_template(self) -> None:
        copyfile("src/cache/cache_template", "sushicache.py")

    def __init__(self) -> None:
        # if cache doesnt exists, create one
        if not self._exists():
            self._copy_template()
