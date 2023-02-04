"""
sushi
"""

import configparser
import sys
from os import path

from rich import print as rich_print

from src.sushipy.config import extends
from src.sushipy.index import find

config = configparser.ConfigParser()
config.read("sushi.conf")


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
            obj = extends.ConfigExtends()
            obj.install()

    def __init__(self) -> None:
        # cleaner way to run multiple functions
        functions = [self._check_config, self._extend_check]
        for f in functions:
            f()

        find()
