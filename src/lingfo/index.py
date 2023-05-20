"""
Gets all functions from another language using tree-sitter
"""

# TODO: clean imports
import configparser
import os

from shutil import rmtree
from contextlib import suppress
from os import mkdir
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

def open_multiple_files():
    """open multiple files (including subfolders)"""

    output = []
    lib_path = config['main']['lib_path'].split('/')[0]

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

                lib_path = config['main']['lib_path'].split('/')[0]
                file_extension = config['main']['lang']
                edited_file = file.replace(f'.{file_extension}', '').replace(f'{lib_path}/', '')
                save(file, edited_file, data)

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

    # remove old files
    with suppress(FileNotFoundError):
        verbose_print('[bold green]lingfo[/bold green]   clearing out/')
        rmtree('out')
        os.makedirs('out')

    files = config["main"]["lib_path"]

    if MULTIPLE_FILES:
        # get all files
        files = open_multiple_files()
        lib_path = config['main']['lib_path'].split('/')[0]

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


def save(full_file_name, file_name, data):
    """saves indexed functions to file"""

    if not exists("out"):
        mkdir("out")


    # create new file
    print_space = " " * 100

    # create missing folders
    file = file_name.split('/')[-1]
    missing_folders = file_name.replace(file, '')

    with suppress(FileExistsError):
        verbose_print('[bold green]lingfo[/bold green]   creating missing folders')
        os.makedirs(f'out/{missing_folders}')

    with open(file=f"out/{file_name}.py", mode="a", encoding="UTF-8") as f:
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
        rich_print(
            f"[bold yellow]lingfo[/bold yellow]   saving indexed function '{data['name']}' ({data['file']}){print_space}"
        )
        # pylint: enable=line-too-long

        fname = data["name"]

        if data["type"] == "function":
            f.write(
                f"def {fname}({data['arg']}):\tExecute('{full_file_name}', \
                    '{data['uuid']}', {data['arg']})\n"
            )
        else:
            variable_name = data["name"].replace(" ", "")
            variable_data = data["variable_data"]

            f.write(
                f"{variable_name} = LingfoVariable('{variable_name}', {variable_data})\n"
            )
        f.close()

        rich_print(
            f"[bold green]lingfo[/bold green]   saved indexed functions to \
out/{file_name}.py{print_space}"
        )
