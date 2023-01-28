"""
executes functions from another language
"""

# pylint: disable=invalid-name, redefined-outer-name, global-statement, missing-class-docstring

import configparser
import inspect
from dataclasses import dataclass
from os import system

config = configparser.ConfigParser()
config.read("sushi.conf")

main_config = config["main"]
launch_config = config["launch"]

TEMP_FILE = ""


@dataclass
class TranslateData:
    import_syntax: str
    file_name: str
    call_function: str


class Execute:
    """executes"""

    def translate(self, data: TranslateData):
        """translates string (multiple replace)"""

        translate_data = {
            "$SUSHI_IMPORT": data.import_syntax.replace("[file-name]", data.file_name),
            "$SUSHI_FUNCTION": data.call_function,
            "$SUSHI_SEMICOLON": ";",
            "$SUSHI_NEWLINE": "\n",
        }

        global TEMP_FILE
        for i, j in translate_data.items():
            TEMP_FILE = TEMP_FILE.replace(i, j)

    def __init__(self) -> None:
        # get from what function was this called
        call_function = inspect.stack()[1].function

        import_syntax = launch_config["import_syntax"]
        file_name = main_config["lib_path"].split("/")[1]

        global TEMP_FILE
        TEMP_FILE = config["temp_file"]["temp_file"]

        data = TranslateData(import_syntax, file_name, call_function)
        self.translate(data)

        self.function()

    def function(self):
        """runs function from another language"""

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

        system("./lib/out")
