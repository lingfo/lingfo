"""
sushi
"""

import configparser
import sys
from os import path
from os.path import isfile

from rich import print as rich_print

from .config import extends
from .index import find

config = configparser.ConfigParser()
config.read("sushi.conf")

# pylint: disable=import-error
if isfile("sushicache.py"):
    import sushicache
# pylint: enable=import-error


class Sushi:
    """sushi"""

    def _check_config(self) -> None:
        if not path.isfile("sushi.conf"):
            rich_print("[bold red]sushi[/bold red]   configuration file doesnt exists")
            sys.exit(1)

    def _extend_check(self) -> None:
        # check if configs needs to be extended

        try:
            config["extends"]["repo"]
        except KeyError:
            pass
        else:
            # skip extend config if it was already extended
            if sushicache.EXTENDS_CONFIG is None:
                obj = extends.ConfigExtends()
                obj.install()

    def __init__(self) -> None:
        # cleaner way to run multiple functions
        functions = [self._check_config, self._extend_check]
        for f in functions:
            f()

        find()
