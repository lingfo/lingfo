"""sushi 0.1"""

import configparser
import os
import platform
import tempfile
from os.path import isfile
from pathlib import Path
from shutil import rmtree

from git import Repo
from rich import print as rich_print

# pylint: disable=import-error, too-few-public-methods
from src.sushipy.cache.main import Cache

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

    def _get_repo(self, data: str, filename: str):
        repourl = f"https://github.com/{data.get('user')}/{data.get('name')}"

        rich_print("[bold yellow]sushi[/bold yellow]   cloning repository")

        # clone repository
        repo = Repo.clone_from(repourl, f"{tempdir}/sushi/")
        repo.git.checkout("main")

        # show what command will be executed from extended config
        temp_config = configparser.ConfigParser()
        temp_config.read(f"{tempdir}/sushi/{filename}")
        exec_command = temp_config["launch"]["exec_command"]

        rich_print(
            f"[bold red]sushi[/bold red]   Extended config will run following command on function execute: {exec_command}. Continue? (Y/N)"
        )

        q = input()

        if q.upper() == "N":
            exit(0)

        # add new config to cache
        with open(f"{tempdir}/sushi/{filename}", "r", encoding="UTF-8") as f:
            Cache.update(
                Cache, "EXTENDS_CONFIG = None", f'EXTENDS_CONFIG = """{f.read()}"""'
            )

        rmtree(f"{tempdir}/sushi/")

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
