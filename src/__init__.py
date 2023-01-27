"""
sushi
"""

import sys
from os import path

from rich import print as rich_print

if not path.isfile("sushi.conf"):
    rich_print("[bold red]sushi[/bold red]   configuration file doesnt exists")
    sys.exit(1)
