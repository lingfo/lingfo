"""Tracks library change with git"""

import subprocess
from contextlib import suppress
from os import chdir, makedirs, name, rename, system
from os.path import isfile
from sys import platform

from rich import print as rich_print

from .cache.main import Cache
from .utils.verbose_print import verbose_print

# pylint: disable=import-error
if isfile("sushicache.py"):
    import sushicache
# pylint: enable=import-error


class GitTracking:
    def _find_changes(self) -> None:
        """returns false if no changes"""

        chdir("lib")
        result = subprocess.run(
            ["git", "--git-dir=.sushi-git", "status"],
            capture_output=True,
            text=True,
        )
        result = result.stdout.split("\n")

        if result[1] == "nothing to commit, working tree clean":
            return False
        else:
            return True

    def _configure_git(self) -> None:
        rich_print(
            "To continue, sushi needs to execute one shell script. If you agree to continue, press any key. Otherwise press N"
        )

        input_data = input()
        if input_data.capitalize() == "N":
            exit(0)

        def v_print(script_name: str):
            verbose_print(
                f"[bold green]sushi[/bold green]   executing script: {script_name}"
            )

        # run script
        if platform == "linux" or platform == "linux2" or platform == "darwin":
            v_print("git_init.sh")
            subprocess.call(
                ["src/sushipy/scripts/git_init.sh", "lib"],
                shell=False,
            )

        elif platform == "win32":
            v_print("git_init.ps1")
            print("windows in progress")

        Cache.update(Cache, "GIT_CONFIGURED = False", "GIT_CONFIGURED = True")

    def __init__(self) -> None:
        with suppress(NameError):
            if sushicache.GIT_CONFIGURED == True:
                return

        self._configure_git()
