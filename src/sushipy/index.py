import configparser
import re
from contextlib import suppress
from os import listdir, mkdir, path
from os.path import exists, isfile

from rich import print as rich_print

from .cache.main import Cache
from .config.auto_detect import TSDetect
from .one_compile import OneCompile
from .stores import MULTIPLE_FILES, ONE_COMPILE
from .utils.find_dict import find as find_dict
from .utils.verbose_print import verbose_print

config = configparser.ConfigParser()
config.read("sushi.conf")

DATA = []


def find():
    detect = TSDetect(
        "cpp",
        """
    #include <iostream>

    void helloWorld(std::string hello) {
        std::cout << "hello world\n";
    }

    void abc(std::string hello) {
        std::cout << "hello world\n";
    }
    """,
    )
    tree = detect.parse_tree().decode("utf-8")
    function_name = tree.split("(")[0]

    function_args = tree.split("(")[1].replace(")", "")
    function_args = function_args.split(" ")[1]

    data = {"name": function_name, "arg": function_args, "file": "lib/another.hpp"}

    if ONE_COMPILE:
        oc_data = OneCompile().setup()
        for x in oc_data:
            if x["name"] == function_name:
                data.__setitem__("uuid", x["uuid"])
    data.__setitem__("uuid", "")

    DATA.append(data)
    save()


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
