"""
sushi
"""

import configparser
import os
import shutil
import sys
from os import path
from os.path import isfile

from git import Repo
from rich import print as rich_print

from .cache.main import Cache
from .config import extends
from .git import GitTracking
from .index import find
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

    def _setup_templates(self) -> None:
        lang = config["main"]["lang"]

        # as for current knowledge, only C++/C uses hpp/h as library file extension
        # so we will only convert that TODO: check if there are more languages

        if lang in ("hpp", "h"):
            lang = "cpp"

        if not os.path.exists(".sushi"):
            os.makedirs(".sushi")

        # setup sushi templates
        verbose_print("[bold green]sushi[/bold green]   cloning sushi templates")
        Repo.clone_from(
            "https://github.com/dev-sushi/language-templates", ".sushi/template-temp/"
        )

        # get template for only user specified language
        shutil.copytree(f".sushi/template-temp/{lang}", f".sushi/template-{lang}")

        with open(
            f".sushi/template-{lang}/if-statement.txt", "r", encoding="utf-8"
        ) as if_statement, open(
            f".sushi/template-{lang}/temp-file.txt", "r", encoding="utf-8"
        ) as temp:
            new_if = if_statement.read().replace("\n", "")
            new_temp = temp.read().replace("\n", "")

            # save to cache
            for i in range(2):
                data_text = "TEMPLATE_IF_STATEMENT" if i == 1 else "TEMPLATE_TEMP_FILE"
                data_var = new_if if i == 1 else new_temp

                Cache.update(
                    Cache, f"{data_text} = None", f'{data_text} = """{data_var}"""'
                )

        verbose_print("[bold green]sushi[/bold green]   cleaning up")
        shutil.rmtree(".sushi/template-temp")
        shutil.rmtree(f".sushi/template-{lang}")

    def __init__(self) -> None:
        verbose_print("[bold green]sushi[/bold green]   checking sushi config ")

        # cleaner way to run multiple functions
        functions = [
            Cache,
            self._check_config,
            self._extend_check,
            GitTracking,
        ]
        for f in functions:
            f()

        find()
