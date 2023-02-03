"""
indexes all files
"""


import configparser
import re
from os import mkdir
from os.path import exists, isfile

from src.sushipy.cache.main import Cache

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
                DATA.append({"type": extract[0], "name": extract[1].split("(")[0]})
        f.close()

    # save indexed functions to cache so we dont have to re-index every launch

    Cache.update(
        Cache,
        f"INDEXED_FUNCTIONS = {sushicache.INDEXED_FUNCTIONS}",
        f"INDEXED_FUNCTIONS = {DATA}",
    )
    save()


def save():
    """saves indexed functions to file"""

    if not exists("out"):
        mkdir("out")

    # create new file
    with open(file="out/main.py", mode="w", encoding="UTF-8") as f:
        f.write("from src.sushipy.execute import Execute\n")

        for x in DATA:
            fname = x["name"]
            f.write(f"def {fname}():\tExecute()\n")
    f.close()
