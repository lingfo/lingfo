"""
sushi
"""

import configparser
import sys
from os import path

from src.config.extends import ConfigExtends

config = configparser.ConfigParser()
config.read("sushi.conf")

from rich import print as rich_print

if not path.isfile("sushi.conf"):
    rich_print("[bold red]sushi[/bold red]   configuration file doesnt exists")
    sys.exit(1)

# check if configs needs to be extended
if config["extends"]["repo"] is not None:
    ConfigExtends.install(ConfigExtends)
