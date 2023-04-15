"""
sushi
"""

import configparser
import sys
from os import path
from os.path import isfile

from rich import print as rich_print

from .cache.main import Cache
from .config import extends
from .git import GitTracking
from .index import find
from .one_compile import OneCompile
from .utils.verbose_print import verbose_print

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
        elif config.getboolean("main", "safe_mode") is False:
            verbose_print(
                "[bold yellow]sushi[/bold yellow]   running with safe_mode turned off!"
            )

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
        verbose_print("[bold green]sushi[/bold green]   checking sushi config ")

        # cleaner way to run multiple functions
        functions = [
            Cache,
            self._check_config,
            self._extend_check,
            GitTracking,
            OneCompile,
        ]
        for f in functions:
            f()

        find()
