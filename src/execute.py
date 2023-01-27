import configparser
import inspect
from os import system

config = configparser.ConfigParser()
config.read("sushi.conf")

main_config = config["main"]
launch_config = config["launch"]

temp_file = ""


class Execute:
    def __init__(self) -> None:
        # get from what function was this called
        call_function = inspect.stack()[1].function

        import_syntax = launch_config["import_syntax"]
        file_name = main_config["lib_path"].split("/")[1]

        translate = {
            "$SUSHI_IMPORT": import_syntax.replace("[file-name]", file_name),
            "$SUSHI_FUNCTION": call_function,
            "$SUSHI_SEMICOLON": ";",
            "$SUSHI_NEWLINE": "\n",
        }

        global temp_file

        temp_file = config["temp_file"]["temp_file"]
        for i, j in translate.items():
            temp_file = temp_file.replace(i, j)
        self.function()

    def function(self):
        # create temporary file
        path = main_config["lib_path"].split("/")[0]
        extension = launch_config["extension"]

        with open(file=f"{path}/temp.{extension}", mode="w") as f:
            f.write(temp_file)
        f.close()

        system(launch_config["exec_command"].replace("[file-name]", "lib/temp.cpp"))
        system("./lib/out")
