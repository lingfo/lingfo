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
if isfile("lingfocache.py"):
    import lingfocache
# pylint: enable=import-error

config = configparser.ConfigParser()
config.read("lingfo.conf")

DATA = []

try:
    CUSTOM_TEMP_FILE = lingfocache.CUSTOM_TEMP_FILE
except NameError:
    CUSTOM_TEMP_FILE = """"""


def _open_find(file):
    """finds all functions"""
    verbose_print(f"[bold green]lingfo[/bold green]   finding functions in {file}")

    with open(file=file, mode="r", encoding="UTF-8") as f:
        lines = f.read()

        detect = TSDetect(
            "cpp",
            lines,
        )

        for x in detect.parse_tree():
            data_x = x["data"]
            tree = data_x.decode("utf-8")

            if x["type"] == "function":
                function_name = tree.split("(")[0]

                function_args = tree.split("(")[1].replace(")", "")
                with suppress(IndexError):
                    function_args = function_args.split(" ")[1]

                data = {
                    "name": function_name,
                    "arg": function_args,
                    "file": file,
                    "type": "function",
                }

                # pylint: disable=unnecessary-dunder-call
                if ONE_COMPILE and lingfocache.INDEXED_FUNCTIONS is not None:
                    oc_data = OneCompile().setup()
                    for data_x in oc_data:
                        if data_x["name"] == function_name:
                            data.__setitem__("uuid", data_x["uuid"])
                data.__setitem__("uuid", "")
                # pylint: enable=unnecessary-dunder-call

                DATA.append(data)
            else:
                # extract variable
                split = tree.split("=")
                name = split[0]
                variable_data = split[1]

                DATA.append(
                    {
                        "type": "variable",
                        "name": name,
                        "variable_data": variable_data,
                        "file": file,
                    }
                )


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
        verbose_print("[bold green]lingfo[/bold green]   updating cache")
        Cache.update(
            Cache,
            f"INDEXED_FUNCTIONS = {lingfocache.INDEXED_FUNCTIONS}",
            f"INDEXED_FUNCTIONS = {DATA}",
        )

    # if old_cache != DATA: TODO: Fix
    # if CUSTOM_TEMP_FILE == """""":
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
                f.write("from src.lingfo.execute import Execute\n")
                f.write("from src.lingfo.utils.variables import LingfoVariable\n")
            else:
                f.write("from lingfo.execute import Execute\n")
                f.write("from lingfo.utils.variables import LingfoVariable\n")

        except configparser.NoOptionError:
            f.write("from lingfo.execute import Execute\n")
            f.write("from lingfo.utils.variables import LingfoVariable\n")

        # Write each function to our created file
        # pylint: disable=line-too-long
        for x in DATA:
            rich_print(
                f"[bold yellow]lingfo[/bold yellow]   saving indexed function '{x['name']}' ({x['file']}){print_space}"
            )
            # pylint: enable=line-too-long

            fname = x["name"]

            if x["type"] == "function":
                f.write(
                    f"def {fname}({x['arg']}):\tExecute('{file_data_old}', \
                        '{x['uuid']}', {x['arg']})\n"
                )
            else:
                variable_name = x["name"].replace(" ", "")
                variable_data = x["variable_data"]

                f.write(
                    f"{variable_name} = LingfoVariable('{variable_name}', {variable_data})\n"
                )
        f.close()

        rich_print(
            f"[bold green]lingfo[/bold green]   saved indexed functions to out/{file_data}.py{print_space}"
        )
