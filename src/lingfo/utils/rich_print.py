"""Wrapper around print from rich library, so it works with quiet mode."""

import configparser
from rich import print as rprint

config = configparser.ConfigParser()
config.read("lingfo.conf")


def rich_print(content: str):
    """wrapper around print from rich library"""

    # off by default

    try:
        if config.getboolean("main", "quiet_mode") is False:
            rprint(content)
    except configparser.NoOptionError:
        rprint(content)
