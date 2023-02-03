"""
sushi
"""

import configparser
import sys
from os import path

from rich import print as rich_print

from src.sushipy.config import extends

config = configparser.ConfigParser()
config.read("sushi.conf")


if not path.isfile("sushi.conf"):
    rich_print("[bold red]sushi[/bold red]   configuration file doesnt exists")
    sys.exit(1)

# check if configs needs to be extended
try:
    config["extends"]["repo"]
except KeyError:
    pass
else:
    obj = extends.ConfigExtends()
    obj.install()
