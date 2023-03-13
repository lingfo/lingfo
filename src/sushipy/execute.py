"""
executes functions from another language
"""

# pylint: disable=invalid-name, redefined-outer-name, missing-class-docstring

import configparser
import inspect
import re
import shlex
import subprocess
from dataclasses import dataclass
from os import remove, system
from os.path import isfile

from .cache.main import Cache
from .stores import ONE_COMPILE

# pylint: disable=import-error
if isfile("sushicache.py"):
    import sushicache
# pylint: enable=import-error


config = configparser.ConfigParser()
config.read("sushi.conf")

main_config = config["main"]
launch_config = config["launch"]

TEMP_FILE = ""
INIT_ARGS = ()


@dataclass
class TranslateData:
    import_syntax: str
    file_name: str
    call_function: str
    args: str


class Execute:
    """executes function"""

    def translate(self, data: TranslateData):
        """translates string (multiple replace)"""

        translate_data = {
            "$SUSHI_IMPORT": data.import_syntax.replace("[file-name]", data.file_name),
            "$SUSHI_FUNCTION": data.call_function,
            "$SUSHI_ARGS": data.args,
            "$SUSHI_SEMICOLON": ";",
            "$SUSHI_NEWLINE": "\n",
        }

        for i, j in translate_data.items():
            self.temp_file = self.temp_file.replace(i, j)

    def __init__(self, *args, **kwargs) -> None:
        self.init_args = INIT_ARGS
        self.temp_file = TEMP_FILE

        # get from what function was this called
        call_function = inspect.stack()[1].function

        self.init_args = re.sub("[()]", "", rf"{args}".replace(",", ""))
        import_syntax = launch_config["import_syntax"]

        file_name = main_config["lib_path"].split("/")[-1]
        if main_config["lib_path"][-1] == "*":
            # user selected multiple files
            file_name = main_config["lib_path"].replace("*", kwargs.get("file"))
            file_name = file_name.split("/")[-1]

        self.temp_file = config["temp_file"]["temp_file"]

        data = TranslateData(import_syntax, file_name, call_function, self.init_args)
        self.translate(data)

        self.function()

    def function(self):
        """runs function from another language"""

        path = main_config["lib_path"].split("/")[0]

        if sushicache.LAST_EXECUTED_CODE == self.temp_file:
            system(f"./{path}/out")
            return

        # create temporary file
        temp_extension = config["temp_file"]["extension"]

        if not ONE_COMPILE:
            with open(
                file=f"{path}/temp.{temp_extension}", mode="w", encoding="UTF-8"
            ) as f:
                f.write(TEMP_FILE)
            f.close()

            subprocess.call(
                shlex.split(
                    launch_config["exec_command"].replace(
                        "[file-name]", f"lib/temp.{temp_extension}"
                    )
                ),
                shell=False,
            )

        Cache.update(
            Cache,
            f"LAST_EXECUTED_CODE = {sushicache.LAST_EXECUTED_CODE}",
            f'LAST_EXECUTED_CODE = """{TEMP_FILE}"""',
        )

        # remove temp file
        if not ONE_COMPILE:
            remove(f"{path}/temp.{temp_extension}")
        subprocess.call([f"./{path}/out"], shell=False)

        return
