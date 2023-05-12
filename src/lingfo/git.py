"""Tracks library change with git"""

import configparser
import os
import subprocess
import sys
from contextlib import suppress
from os import chdir
from os.path import isfile
from sys import platform

from rich import print as rich_print

from .cache.main import Cache
from .utils.verbose_print import verbose_print

# pylint: disable=import-error
if isfile("lingfocache.py"):
    import lingfocache
# pylint: enable=import-error

config = configparser.ConfigParser()
config.read("lingfo.conf")


class GitTracking:
    """git tracking"""

    def _find_changes(self) -> None:
        """returns False if no changes"""

        if not isfile("lingfocache.py"):
            return False

        chdir("lib")
        result = subprocess.run(
            ["git", "--git-dir=.lingfo-git", "status"],
            capture_output=True,
            text=True,
            check=True,
        )
        result = result.stdout.split("\n")

        return result[1] == "nothing to commit, working tree clean"

    def _configure_git(self) -> None:
        with suppress(KeyError):
            if config.getboolean("main", "safe_mode") is True:
                rich_print(
                    "To continue, lingfo needs to execute one shell script. "
                    + "If you agree to continue, press any key. Otherwise press N"
                )

                input_data = input()
                if input_data.capitalize() == "N":
                    sys.exit(0)

        def v_print(script_name: str):
            verbose_print(
                f"[bold green]lingfo[/bold green]   executing script: {script_name}"
            )

        # run script
        if platform in ("linux", "linux2", "darwin"):
            v_print("git_init.sh")

            current_path = os.path.dirname(__file__)
            path = os.path.abspath(str(current_path) + "/scripts/git_init.sh")
            os.system(f"chmod +x {path}")
            subprocess.call(
                [path, "lib"],
                stdout=subprocess.DEVNULL,
                shell=False,
            )

        elif platform == "win32":
            v_print("git_init.ps1")
            print("windows in progress! report any issues on github")

            current_path = os.path.dirname(__file__)
            path = os.path.abspath(str(current_path) + "/scripts/git_init.ps1")
            subprocess.call(
                [path, "lib"],
                stdout=subprocess.DEVNULL,
                shell=False,
            )

        Cache.update(Cache, "GIT_CONFIGURED = False", "GIT_CONFIGURED = True")

    def __init__(self) -> None:
        with suppress(NameError):
            if lingfocache.GIT_CONFIGURED is True:
                return

        self._configure_git()
