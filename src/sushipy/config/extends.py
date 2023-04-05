"""sushi 0.1"""

import configparser
import os
import platform
import pydoc
import sys
import tempfile
from os.path import isfile
from pathlib import Path
from shutil import rmtree

from git import Repo
from rich import print as rich_print

# pylint: disable=import-error, too-few-public-methods
from ..cache.main import Cache

# from utils.verbose_print import verbose_print TODO

if isfile("sushicache.py"):
    import sushicache
# pylint: enable=import-error


config = configparser.ConfigParser()
config.read("sushi.conf")

# get temp and current path
tempdir = Path("/tmp" if platform.system() == "Darwin" else tempfile.gettempdir())
currentpath = os.path.dirname(os.path.realpath(__file__))


class ConfigExtends:
    """extends config from another config"""

    def _parse_repo(
        self,
        repo: str,
    ) -> dict[str, str]:  # pylint disable=unsubscriptable-object
        """parse repo config

        example:
        from: `@dev-sushi/example`
        to: `https://github.com/dev-sushi/example`
        """

        # this string contains 2 parts: user, repository name seperated with /
        newrepo = repo.replace("@", "")
        split: str = newrepo.split("/")
        return {"user": split[0], "name": split[1]}

    def _review_config(self, filename: str):
        rich_print("[bold red]sushi[/bold red]   review configuration!")

        with open(f"{tempdir}/sushi/{filename}", "r", encoding="UTF-8") as f:
            content = f.read()
        pydoc.pager(content)

        # rich_print(
        #     "[bold red]sushi[/bold red]   Press C to cancel, otherwise press any other key."
        # )

        out = input()

        if out.upper() == "C":
            rmtree(f"{tempdir}/sushi/")
            sys.exit(0)

    def _get_repo(self, data: str, filename: str):
        repourl = f"https://github.com/{data.get('user')}/{data.get('name')}"

        # verbose_print(f"[bold green]sushi[/bold green]   cloning repository {repourl}")

        # clone repository
        repo = Repo.clone_from(repourl, f"{tempdir}/sushi/")
        repo.git.checkout("main")

        # show what command will be executed from extended config
        temp_config = configparser.ConfigParser()
        temp_config.read(f"{tempdir}/sushi/{filename}")

        if config.getboolean("main", "safe_mode") is True:
            self._review_config(filename)

        # add new config to cache
        with open(f"{tempdir}/sushi/{filename}", "r", encoding="UTF-8") as f:
            Cache.update(
                Cache, "EXTENDS_CONFIG = None", f'EXTENDS_CONFIG = """{f.read()}"""'
            )

        rmtree(f"{tempdir}/sushi/")
        # verbose_print(
        #     f"[bold green]sushi[/bold green]   removing file {tempdir}/sushi/"
        # )

    def install(self):
        """installs custom config"""

        repo: str = config["extends"]["repo"]
        filename: str = config["extends"]["file"]

        data = self._parse_repo(repo)
        self._get_repo(data, filename)


class MergeConfig:
    """copies extended config and adds it to sushi.conf"""

    def _get_config(self):
        with open("sushi.conf", encoding="UTF-8") as f:
            data = f.read()
            return data

    def __init__(self) -> None:
        # get extended config and sushi.conf config
        ext_config = sushicache.EXTENDS_CONFIG
        original_config = self._get_config()

        # add 2 configs together
        original_config += ext_config
