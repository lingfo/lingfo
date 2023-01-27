from os import path

from rich import print

if not path.isfile("sushi.conf"):
    print("[bold red]sushi[/bold red]   configuration file doesnt exists")
    exit(1)
