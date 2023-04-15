"""
Gets all functions from another language using tree-sitter
"""

import configparser
from contextlib import suppress
from os import listdir, mkdir, path
from os.path import exists, isfile

from rich import print as rich_print

from .cache.main import Cache
from .config.auto_detect import TSDetect
from .one_compile import OneCompile
from .stores import MULTIPLE_FILES, ONE_COMPILE
from .utils.verbose_print import verbose_print

# pylint: disable=import-error
if isfile("sushicache.py"):
    import sushicache
# pylint: enable=import-error

config = configparser.ConfigParser()
config.read("sushi.conf")

DATA = []

try:
    CUSTOM_TEMP_FILE = sushicache.CUSTOM_TEMP_FILE
except NameError:
    CUSTOM_TEMP_FILE = """"""


def _open_find(file):
    """finds all functions by using regex from sushi.conf"""
    verbose_print(
        f"[bold green]sushi[/bold green]   finding functions in {file} from sushi.conf"
    )

    with open(file=file, mode="r", encoding="UTF-8") as f:
        lines = f.read()

        detect = TSDetect(
            "cpp",
            lines,
        )

        for x in detect.parse_tree():
            tree = x.decode("utf-8")
            function_name = tree.split("(")[0]

            function_args = tree.split("(")[1].replace(")", "")
            with suppress(IndexError):
                function_args = function_args.split(" ")[1]

            data = {
                "name": function_name,
                "arg": function_args,
                "file": file,
            }

            # pylint: disable=unnecessary-dunder-call
            if ONE_COMPILE:
                oc_data = OneCompile().setup()
                for x in oc_data:
                    if x["name"] == function_name:
                        data.__setitem__("uuid", x["uuid"])
            data.__setitem__("uuid", "")
            # pylint: enable=unnecessary-dunder-call

            DATA.append(data)


def find():
    """finds functions"""

    files = config["main"]["lib_path"]

    if MULTIPLE_FILES:
        # get all files
        lib_path = path.relpath(files.replace("*", ""))
        all_files = listdir(lib_path)

        with suppress(ValueError):
            all_files.remove("out")

        for x in all_files:
            _open_find(lib_path + "/" + x)
    else:
        _open_find(files)

    # save indexed functions to cache so we dont have to re-index every launch
    with suppress(NameError):
        verbose_print("[bold green]sushi[/bold green]   updating cache")
        Cache.update(
            Cache,
            f"INDEXED_FUNCTIONS = {sushicache.INDEXED_FUNCTIONS}",
            f"INDEXED_FUNCTIONS = {DATA}",
        )

    # if old_cache != DATA:
    if CUSTOM_TEMP_FILE == """""":
        save()

    return DATA


def save():
    """saves indexed functions to file"""

    if not exists("out"):
        mkdir("out")

    # create new file
    file_data_old = DATA[0]["file"].split("/")[-1]
    file_data = file_data_old.replace("." + config["main"]["lang"], "")

    print_space = " " * 100

    with open(file=f"out/{file_data}.py", mode="w", encoding="UTF-8") as f:
        # TODO: cleanup
        try:
            if config.getboolean("index", "dev"):
                f.write("from src.sushipy.execute import Execute\n")
            else:
                f.write("from sushipy.execute import Execute\n")

        except configparser.NoOptionError:
            f.write("from sushipy.execute import Execute\n")

        # Write each function to our created file
        # pylint: disable=line-too-long
        for x in DATA:
            rich_print(
                f"[bold yellow]sushi[/bold yellow]   saving indexed function '{x['name']}' ({x['file']}){print_space}"
            )
            # pylint: enable=line-too-long

            fname = x["name"]

            f.write(
                f"def {fname}({x['arg']}):\tExecute('{file_data_old}', '{x['uuid']}', {x['arg']})\n"
            )

        f.close()

        rich_print(
            f"[bold green]sushi[/bold green]   saved indexed functions to out/{file_data}.py{print_space}"
        )
