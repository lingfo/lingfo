"""
Gets all functions from another language using tree-sitter
"""

# TODO: clean imports
import configparser
import os

from shutil import rmtree
from contextlib import suppress
from pathlib import Path

from os import mkdir
from os.path import exists, isfile

from .utils.rich_print import rich_print

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


def open_multiple_files():
    """open multiple files (including subfolders)"""

    output = []
    lib_path = config["main"]["lib_path"].split("/")[0]

    for path, _subdirs, files in os.walk(lib_path + "/"):
        for name in files:
            output.append(os.path.join(path, name))

    return output


def _open_find(file):
    """finds all functions"""
    verbose_print(f"[bold green]lingfo[/bold green]   finding functions in {file}")

    with open(file=file, mode="r", encoding="UTF-8") as f:
        lines = f.read()

        detect = TSDetect(
            "cpp",
            lines,
        )

        parse_tree = detect.parse_tree()
        tree_data = []

        # remove multiple arrays in output
        for x in parse_tree:
            if isinstance(x, list):
                # TODO: try to omit nested for loops
                for y in x:
                    tree_data.append(y)
            else:
                tree_data.append(x)

        for x in tree_data:
            data_x = x["data"]
            tree = data_x.decode("utf-8")

            if x["type"] == "function":
                # skip wrong file extension
                file_split = file.split(".")
                if file_split[-1] != config["main"]["lang"]:
                    verbose_print(
                        "[bold red]lingfo[/bold red]   wrong file extension, skipping."
                    )
                    return
                function_name = tree.split("(")[0]

                function_args = tree.split("(")[1].replace(")", "")
                with suppress(IndexError):
                    function_args = function_args.split(" ")[1]

                data = {
                    "name": function_name,
                    "arg": function_args,
                    "file": file,
                    "type": "function",
                    "from": x["from"],
                }

                try:
                    class_name_data = {"class_name": x["class_name"]}
                except KeyError:
                    class_name_data = {"class_name": ""}

                data = {**data, **class_name_data}

                # pylint: disable=unnecessary-dunder-call
                if ONE_COMPILE and lingfocache.INDEXED_FUNCTIONS is not None:
                    oc_data = OneCompile().setup()
                    for data_x in oc_data:
                        if data_x["name"] == function_name:
                            data.__setitem__("uuid", data_x["uuid"])
                data.__setitem__("uuid", "")
                # pylint: enable=unnecessary-dunder-call

                DATA.append(data)

                lib_path = config["main"]["lib_path"].split("/")[0]
                file_extension = config["main"]["lang"]
                edited_file = file.replace(f".{file_extension}", "").replace(
                    f"{lib_path}/", ""
                )
                save(file, edited_file, data)
            else:
                # extract variable
                split = tree.split("=")
                name = split[0]
                variable_data = split[1]

                try:
                    x["class_name"]
                except KeyError:
                    x["class_name"] = ""

                DATA.append(
                    {
                        "type": "variable",
                        "name": name,
                        "variable_data": variable_data,
                        "file": file,
                        "from": x["from"],
                        "class_name": x["class_name"],
                    }
                )


def find():
    """finds functions"""

    # remove old files
    with suppress(FileNotFoundError):
        verbose_print("[bold green]lingfo[/bold green]   clearing out/")
        rmtree("out")
        os.makedirs("out")

    files = config["main"]["lib_path"]

    if MULTIPLE_FILES:
        # get all files
        files = open_multiple_files()
        lib_path = config["main"]["lib_path"].split("/")[0]

        with suppress(ValueError):
            files.remove(f"{lib_path}/out")

        for x in files:
            _open_find(x)
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

    return DATA


saved_classes = []


def save(full_file_name, file_name, data):
    """saves indexed functions to file"""

    def save_class():
        class_name = data["class_name"]
        class_spaces = "\t\t\t"
        return f'class {class_name}():\n\
\t\tdef __init__(self):\n\
{class_spaces}"""Lingfo class"""\n\
{class_spaces}pass\n'

    if not exists("out"):
        mkdir("out")

    def save_function(in_class: bool = False):
        spaces = "\t\t" if in_class else ""
        class_name = data["class_name"] if in_class else ""
        use_self = "self," if in_class else ""

        return f"{spaces}def {fname}({use_self}{data['arg']}):\tExecute('{full_file_name}', \
                        '{data['uuid']}', {in_class}, '{class_name}', {data['arg']})\n"

    # create new file
    print_space = " " * 100

    # create missing folders
    with suppress(FileExistsError):
        verbose_print("[bold green]lingfo[/bold green]   creating missing folders")
        os.makedirs(f"out/{file_name}")

    with open(file=f"out/{file_name}.py", mode="a+", encoding="UTF-8") as f:
        f_temp = f
        f_temp.seek(0)

        # TODO: cleanup
        if len(f_temp.readlines()) == 0:
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
        rich_print(
            f"[bold yellow]lingfo[/bold yellow]   saving indexed function '{data['name']}' ({data['file']}){print_space}"
        )
        # pylint: enable=line-too-long

        fname = data["name"]

        if data["from"] == "file":
            if data["type"] == "function":
                f.write(save_function())
            elif data["type"] == "variable":
                variable_name = data["name"].replace(" ", "")
                variable_data = data["variable_data"]

                f.write(
                    f"{variable_name} = LingfoVariable('{variable_name}', {variable_data})\n"
                )

        # save class
        if data["from"] == "class":
            if not data["class_name"] in saved_classes:
                saved_classes.append(data["class_name"])
                f.write(save_class())

            if data["type"] == "function":
                f.write(save_function(True))
        f.close()

        rich_print(
            f"[bold green]lingfo[/bold green]   saved indexed functions to \
out/{file_name}.py{print_space}"
        )

    verbose_print(
        "[bold green]lingfo[/bold green]   removing empty directories in out/"
    )

    # remove empty directories that were probably created by accident
    for root, directories, _ in os.walk("out", topdown=False):
        for x in directories:
            with suppress(OSError):
                os.rmdir(Path(root, x))
