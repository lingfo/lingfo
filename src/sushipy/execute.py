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
from .utils.verbose_print import verbose_print

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


class MultipleExecute:
    def __init__(self, name: str = "default") -> None:
        self.state_name = name

    # def set_name(self, name: str):
    #     """sets name for current 'state'. This is optional but might be useful when
    #     dealing with functions saved for later"""

    #     self.state_name = name

    def save(self, function_name: str, function_path: str, function_arguments: any):
        """saves function to launch it later"""

        with open(
            f".sushi/multiple-execute-{self.state_name}.txt", "a", encoding="UTF-8"
        ) as f:
            # PATH:NAME:ARGUMENTS
            f.write(f"{function_path}:{function_name}:{str(function_arguments)}\n")

    def _open_file(self):
        f = open(
            f".sushi/multiple-execute-{self.state_name}.txt", "r", encoding="UTF-8"
        )

        return f

    def _guess_function(self, content):
        """Tries to guess how to extract only function call from file (or another function).
        This wont work all of the times, so report any issues on github.
        """

        # as for current knowledge, no language calls thier function with {}
        if "{" in content:
            # probably dealing with compiled language
            new = content.split("{")[1]
            new = new.replace("}", "").replace(";", "")

            return new
        # TODO: add support for interpreted languages

    def __enter__(self, *args):
        print("enter")

    def __exit__(self, *args):
        file = self._open_file()
        lines = file.readlines()

        execute = Execute(None, None, None, use_multiple_execute=True)

        output = []
        for x in lines:
            # read from line
            split = x.split(":")

            file_split = split[0]
            function = split[1]
            args = split[2]

            # get import syntax from config (TODO: its already defined somewhere else)
            if config.getboolean("main", "use_templates") is True:
                import_syntax = sushicache.TEMPLATE_IMPORT_SYNTAX
                temp_file = sushicache.TEMPLATE_TEMP_FILE
            else:
                import_syntax = launch_config["import_syntax"]
                temp_file = config["temp_file"]["temp_file"]

            data = TranslateData(import_syntax, file_split, function, args)

            output.append(
                execute.translate(
                    data,
                    temp_file,
                    True,
                )
            )

            self._guess_function("int main() {hello();}")

            # execute it
            # execute.function("", output=output)

        file.close()

        # remove temp file
        remove(f".sushi/multiple-execute-{self.state_name}.txt")


class Execute:
    """executes function"""

    def translate(self, data: TranslateData, temp_file="", use_multiple_execute=False):
        """translates string (multiple replace)"""

        self.temp_file = temp_file

        # modify args to only keep the second argument
        if data.args:
            args_list = data.args.split()
            if len(args_list) >= 1:
                args = args_list[0]
            else:
                args = ""
        else:
            args = ""

        translate_data = {
            "$SUSHI_IMPORT": data.import_syntax.replace("[file-name]", data.file_name),
            "$SUSHI_FUNCTION": data.call_function,
            "$SUSHI_ARGS": args,
            "$SUSHI_SEMICOLON": ";",
            "$SUSHI_NEWLINE": "\n",
        }

        # TODO: cleanup
        for i, j in translate_data.items():
            self.temp_file = self.temp_file.replace(i, j)

        return self.temp_file

    def __init__(self, file, uuid, *args, use_multiple_execute=False) -> None:
        self.temp_file = ""

        if use_multiple_execute is True:
            return

        self.init_args = INIT_ARGS
        self.temp_file = TEMP_FILE

        # get from what function was this called
        if sushicache.CUSTOM_TEMP_FILE is None:
            call_function = inspect.stack()[1].function
        else:
            call_function = sushicache.CUSTOM_TEMP_FILE

        call_function = inspect.stack()[1].function
        verbose_print(
            f"[bold green]sushi[/bold green]   finding function {call_function}"
        )

        self.init_args = re.sub("[()]", "", rf"{args}".replace(",", ""))
        if config.getboolean("main", "use_templates") is True:
            import_syntax = sushicache.TEMPLATE_IMPORT_SYNTAX
        else:
            import_syntax = launch_config["import_syntax"]
        file_name = main_config["lib_path"].split("/")[-1]
        if main_config["lib_path"][-1] == "*":
            # user selected multiple files
            file_name = main_config["lib_path"].replace("*", file)
            file_name = file_name.split("/")[-1]

        if config.getboolean("main", "use_templates") is True:
            self.temp_file = sushicache.TEMPLATE_TEMP_FILE
        else:
            self.temp_file = config["temp_file"]["temp_file"]

        if ONE_COMPILE:
            # if () is in temp file remove it
            delimiter = "SUSHI_FUNCTION"

            index = self.temp_file.find(delimiter)
            after = self.temp_file[index + len(delimiter) :]

            # TODO: cleanup!
            after = (
                after.replace("$SUSHI_ARGS", "")
                .replace("$SUSHI_SEMICOLON", "")
                .replace("}", "")
            )

            if after == "()":
                self.temp_file = self.temp_file.replace("($SUSHI_ARGS)", "")

        data = TranslateData(import_syntax, file_name, call_function, self.init_args)
        self.translate(data)

        if config.getboolean("launch", "multiple_functions") is True:
            multiple_execute = MultipleExecute()
            multiple_execute.save(call_function, file, self.init_args)
        else:
            self.function(uuid)

    def function(self, uuid, output=None):
        """runs function from another language"""

        path = main_config["lib_path"].split("/")[0]

        if sushicache.LAST_EXECUTED_CODE == self.temp_file and ONE_COMPILE is False:
            system(f"./{path}/out")
            return

        # create temporary file
        temp_extension = config["temp_file"]["extension"]

        def execute_prelaunch():
            with open(
                file=f"{path}/temp.{temp_extension}", mode="w", encoding="UTF-8"
            ) as f:
                # we can check if multiple execute was used using type check
                if isinstance(output, list):
                    for x in output:
                        f.write(x + "\n")
                else:
                    f.write(self.temp_file)
            f.close()

            # should print the function name for debugging purposes
            verbose_print("[bold green]sushi[/bold green]   executing function ")
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

        # we should skip it if using one (time) compile
        if ONE_COMPILE is False:
            execute_prelaunch()

        print(uuid)
        # remove temp file
        remove(f"{path}/temp.{temp_extension}")
        subprocess.call([f"./{path}/out", uuid], shell=False)
