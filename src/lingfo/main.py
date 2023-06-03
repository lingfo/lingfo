"""
lingfo
"""

import configparser
import os
import shutil
import sys
from os import path
from os.path import isfile

from git import Repo
from .utils.rich_print import rich_print

from .cache.main import Cache
from .config import extends
from .index import find
from .utils.verbose_print import verbose_print

config = configparser.ConfigParser()
config.read("lingfo.conf")


# pylint: disable=import-error
if isfile("lingfocache.py"):
    import lingfocache
# pylint: enable=import-error


class Lingfo:
    """lingfo"""

    def _check_config(self) -> None:
        if not path.isfile("lingfo.conf"):
            rich_print("[bold red]lingfo[/bold red]   configuration file doesnt exists")
            sys.exit(1)
        elif config.getboolean("main", "safe_mode") is False:
            verbose_print(
                "[bold yellow]lingfo[/bold yellow]   running with safe_mode turned off!"
            )

    def _extend_check(self) -> None:
        # check if configs needs to be extended

        try:
            config["extends"]["repo"]
        except KeyError:
            pass
        else:
            # skip extend config if it was already extended
            if lingfocache.EXTENDS_CONFIG is None:
                obj = extends.ConfigExtends()
                obj.install()

    def _setup_templates(self) -> None:
        if config.getboolean("main", "use_templates") is False:
            return

        lang = config["main"]["lang"]

        # as for current knowledge, only C++/C uses hpp/h as library file extension
        # so we will only convert that TODO: check if there are more languages

        if lang in ("hpp", "h"):
            lang = "cpp"

        if not os.path.exists(".lingfo"):
            os.makedirs(".lingfo")

        # setup lingfo templates
        verbose_print("[bold green]lingfo[/bold green]   cloning lingfo templates")
        Repo.clone_from(
            "https://github.com/dev-lingfo/language-templates", ".lingfo/template-temp/"
        )

        # get template for only user specified language
        shutil.copytree(f".lingfo/template-temp/{lang}", f".lingfo/template-{lang}")

        # TODO: cleanup required!
        with open(
            f".lingfo/template-{lang}/if-statement.txt", "r", encoding="utf-8"
        ) as if_statement, open(
            f".lingfo/template-{lang}/temp-file.txt", "r", encoding="utf-8"
        ) as temp, open(
            f".lingfo/template-{lang}/import-syntax.txt", "r", encoding="utf-8"
        ) as import_syntax:
            new_if = if_statement.read().replace("\n", "")
            new_temp = temp.read().replace("\n", "")
            import_syntax = import_syntax.read().replace("\n", "")

            # save to cache
            for i in range(3):
                if i == 1:
                    data_text = "TEMPLATE_IF_STATEMENT"
                    data_var = new_if
                elif i == 2:
                    data_text = "TEMPLATE_TEMP_FILE"
                    data_var = new_temp
                else:
                    data_text = "TEMPLATE_IMPORT_SYNTAX"
                    data_var = import_syntax

                Cache.update(
                    Cache, f"{data_text} = None", f'{data_text} = """{data_var}"""'
                )

        verbose_print("[bold green]lingfo[/bold green]   cleaning up")
        shutil.rmtree(".lingfo/template-temp")
        shutil.rmtree(f".lingfo/template-{lang}")

    def __init__(self) -> None:
        verbose_print("[bold green]lingfo[/bold green]   checking lingfo config ")

        # cleaner way to run multiple functions
        functions = [
            Cache,
            self._check_config,
            self._extend_check,
        ]
        for f in functions:
            f()

        find()
