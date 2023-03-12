"""
indexes all files
"""


import configparser
import re
from contextlib import suppress
from os import listdir, mkdir, path
from os.path import exists, isfile

from rich import print as rich_print

from .cache.main import Cache
from .stores import MULTIPLE_FILES
from .utils.find_dict import find as find_dict

# pylint: disable=import-error
if isfile("sushicache.py"):
    import sushicache
# pylint: enable=import-error

config = configparser.ConfigParser()
config.read("sushi.conf")

DATA = []


def _open_find(
    file,
    function_pattern,
):
    """finds all functions by using regex from sushi.conf"""

    # first, open file
    with open(file=file, mode="r", encoding="UTF-8") as f:
        lines = f.read().split("\n")

        # now, loop through all lines to see if there are any functions
        for x in lines:
            f_pattern = re.compile(function_pattern, re.IGNORECASE)
            extract = x.split()

            if f_pattern.match(x):
                # append to data
                name = extract[1].split("(")[0]
                data = {"type": extract[0], "name": name, "all": extract, "file": file}

                # get arguments from functions and save it
                # pylint: disable=unsupported-binary-operation
                arg_data = get_arg(name, data)
                DATA.append(data | {"arg": arg_data})
                # pylint: enable=unsupported-binary-operation

        f.close()


def find():
    """finds functions"""

    function_pattern = config["index"]["function_pattern"]
    files = config["main"]["lib_path"]

    if MULTIPLE_FILES:
        # get all files
        lib_path = path.relpath(files.replace("*", ""))

        all_files = listdir(lib_path)
        all_files.remove("out")

        for x in all_files:
            _open_find(lib_path + "/" + x, function_pattern)
    else:
        _open_find(files, function_pattern)

    # save indexed functions to cache so we dont have to re-index every launch
    with suppress(NameError):
        Cache.update(
            Cache,
            f"INDEXED_FUNCTIONS = {sushicache.INDEXED_FUNCTIONS}",
            f"INDEXED_FUNCTIONS = {DATA}",
        )

    # if old_cache != DATA:
    save()

    return DATA


def save():
    """saves indexed functions to file"""

    if not exists("out"):
        mkdir("out")

    # create new file
    file_data_old = DATA[0]['file'].split("/")[-1]
    file_data = file_data_old.replace("." + config["main"]["lang"], "")

    with open(file=f"out/{file_data}.py", mode="w", encoding="UTF-8") as f:
        f.write("from sushipy.execute import Execute\n")

        # Write each function to our created file
        for x in DATA:
            rich_print(
                f"[bold yellow]sushi[/bold yellow]   saving indexed functions ({x.get('file')})"
            )

            fname = x["name"]

            args = ""
            if "arg" in x and x["arg"] is not None:
                args = x["arg"][0]
                if len(x["arg"]) > 1:
                    args = ",".join(x["arg"][1:])

            f.write(f"def {fname}({args}):\tExecute('{file_data_old}', {args})\n")

        f.close()


def get_arg(name: str, data: any):
    """gets all arguments from function"""

    args = []
    find_data = find_dict(name, [data], "name")

    extract_data = find_data.get("all")

    with suppress(IndexError):
        split_args = extract_data[2]

        if split_args[-1] == ",":
            # there are more arguments than 1

            i = 2
            multiple_args = []

            while True:
                try:
                    multiple_args.append(extract_data[i])

                    i += (
                        2
                        if config.getboolean("index", "variables_contains_types")
                        else 1
                    )

                except IndexError:
                    # remove )
                    last_item = multiple_args[-1]
                    multiple_args.pop()
                    multiple_args.append(last_item.replace(")", ""))

                    return multiple_args

        elif split_args != ")":
            args.append(split_args.replace(")", ""))

        return args
