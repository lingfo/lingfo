"""
executes functions from another language
"""

# pylint: disable=invalid-name, redefined-outer-name, global-statement, missing-class-docstring

import configparser
import inspect
import re
from dataclasses import dataclass
from os import remove, system
from os.path import isfile

from .cache.main import Cache

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


class Execute:
    """executes function"""

    def translate(self, data: TranslateData):
        """translates string (multiple replace)"""

        translate_data = {
            "$SUSHI_IMPORT": data.import_syntax.replace("[file-name]", data.file_name),
            "$SUSHI_FUNCTION": data.call_function,
            "$SUSHI_ARGS": INIT_ARGS,
            "$SUSHI_SEMICOLON": ";",
            "$SUSHI_NEWLINE": "\n",
        }

        global TEMP_FILE
        for i, j in translate_data.items():
            TEMP_FILE = TEMP_FILE.replace(i, j)

    def __init__(self, *args) -> None:
        global INIT_ARGS

        # get from what function was this called
        call_function = inspect.stack()[1].function

        INIT_ARGS = re.sub("[()]", "", rf"{args}".replace(",", ""))
        import_syntax = launch_config["import_syntax"]
        file_name = main_config["lib_path"].split("/")[1]

        global TEMP_FILE
        TEMP_FILE = config["temp_file"]["temp_file"]

        data = TranslateData(import_syntax, file_name, call_function)
        self.translate(data)

        self.function()

    def function(self):
        """runs function from another language"""

        if sushicache.LAST_EXECUTED_CODE == TEMP_FILE:
            system("./lib/out")
            return

        # create temporary file
        path = main_config["lib_path"].split("/")[0]
        temp_extension = config["temp_file"]["extension"]

        with open(
            file=f"{path}/temp.{temp_extension}", mode="w", encoding="UTF-8"
        ) as f:
            f.write(TEMP_FILE)
        f.close()

        system(
            launch_config["exec_command"].replace(
                "[file-name]", f"lib/temp.{temp_extension}"
            )
        )

        Cache.update(
            Cache,
            f"LAST_EXECUTED_CODE = {sushicache.LAST_EXECUTED_CODE}",
            f'LAST_EXECUTED_CODE = """{TEMP_FILE}"""',
        )

        # remove temp file
        remove(f"lib/temp.{temp_extension}")
        system("./lib/out")

        return
