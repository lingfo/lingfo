"""
indexes all files
"""


import configparser
import re
from contextlib import suppress
from os import mkdir
from os.path import exists, isfile

from rich import print as rich_print

from .cache.main import Cache
from .utils.find_dict import find as find_dict

# pylint: disable=import-error
if isfile("sushicache.py"):
    import sushicache
# pylint: enable=import-error


config = configparser.ConfigParser()
config.read("sushi.conf")

DATA = []


def find():
    """finds all functions by using regex from sushi.conf"""
    function_pattern = config["index"]["function_pattern"]

    files = config["main"]["lib_path"]

    # first, open file
    with open(file=files, mode="r", encoding="UTF-8") as f:
        lines = f.read().split("\n")

        # now, loop through all lines to see if there are any functions
        for x in lines:
            f_pattern = re.compile(function_pattern, re.IGNORECASE)
            extract = x.split()

            if f_pattern.match(x):
                # append to data
                name = extract[1].split("(")[0]
                DATA.append(
                    {
                        "type": extract[0],
                        "name": name,
                        "all": extract,
                    }
                )

                # get arguments from functions and save it
                arg_data = get_arg(name)
                DATA.append(DATA[0] | {"arg": arg_data})

        f.close()

    # save indexed functions to cache so we dont have to re-index every launch
    Cache.update(
        Cache,
        f"INDEXED_FUNCTIONS = {sushicache.INDEXED_FUNCTIONS}",
        f"INDEXED_FUNCTIONS = {DATA}",
    )

    # if old_cache != DATA:
    save()


def save():
    """saves indexed functions to file"""

    rich_print("[bold yellow]sushi[/bold yellow]   saving indexed functions")
    if not exists("out"):
        mkdir("out")

    # create new file
    with open(file="out/main.py", mode="w", encoding="UTF-8") as f:
        f.write("from sushipy.execute import Execute\n")

        print(DATA)
        for x in DATA:
            fname = x["name"]
            f.write(f"def {fname}():\tExecute()\n")
    f.close()


def get_arg(name: str):
    """gets all arguments from function"""

    args = []
    find_data = find_dict(name, DATA, "name")

    extract_data = find_data.get("all")

    with suppress(IndexError):
        split_args = extract_data[2]

        if split_args != ")":
            args.append(split_args.replace(")", ""))

        return args
