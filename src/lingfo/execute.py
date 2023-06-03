"""
executes functions from another language
"""

# pylint: disable=invalid-name, redefined-outer-name, missing-class-docstring

import configparser
import inspect
import re
import shlex
import subprocess
import sys

from random import choices
from string import ascii_lowercase

from dataclasses import dataclass
from os import remove
from os.path import isfile
from .utils.rich_print import rich_print

from .cache.main import Cache
from .stores import ONE_COMPILE
from .utils.verbose_print import verbose_print

# pylint: disable=import-error
if isfile("lingfocache.py"):
    import lingfocache
# pylint: enable=import-error


config = configparser.ConfigParser()
config.read("lingfo.conf")

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
    is_class: bool


class MultipleExecute:
    def __init__(self, name: str = "default") -> None:
        if config.getboolean("launch", "multiple_functions") is False:
            rich_print(
                "[bold red]lingfo[/bold red]   running multiple_functions mode when \
this is turned off in settings! Please turn it back on in lingfo.conf before continuing."
            )
            sys.exit(1)
        self.state_name = name

    def save(
        self,
        function_type: str,
        function_name: str,
        function_path: str,
        function_arguments: any,
    ):
        """saves function to launch it later"""

        with open(
            f".lingfo/multiple-execute-{self.state_name}.txt", "a", encoding="UTF-8"
        ) as f:
            # TYPE:PATH:NAME:ARGUMENTS
            f.write(
                f"{function_type}:{function_path}:{function_name}:{str(function_arguments)}\n"
            )

    def _open_file(self):
        """opens file"""

        # pylint: disable=consider-using-with
        f = open(
            f".lingfo/multiple-execute-{self.state_name}.txt", "r", encoding="UTF-8"
        )
        # pylint: enable=consider-using-with

        return f

    def __enter__(self, *args_function):
        pass

    def launch(self):
        """launch functions"""

        file = self._open_file()
        lines = file.readlines()

        execute = Execute(None, None, None, use_multiple_execute=True, class_name="")

        # get import syntax from config (TODO: its already defined somewhere else)
        if config.getboolean("main", "use_templates") is True:
            import_syntax = lingfocache.TEMPLATE_IMPORT_SYNTAX
            temp_file = lingfocache.TEMPLATE_TEMP_FILE
        else:
            import_syntax = launch_config["import_syntax"]
            temp_file = config["temp_file"]["temp_file"]

        functions = ""

        file_split, function, args = "", "", ""

        for x in lines:
            # read from line
            split = x.split(":")

            # function_type = split[0]
            file_split = split[1]
            function = split[2]
            args = split[3]

            # TODO: add support for languages without semicolon

            functions += str(function)
        file.close()

        # translate it
        data = TranslateData(import_syntax, file_split, functions, args, is_class=False)
        output = execute.translate(
            data,
            temp_file,
        )

        # execute it
        execute.function("", output=output)

        # remove temp file
        remove(f".lingfo/multiple-execute-{self.state_name}.txt")

    def __exit__(self, *args_function):
        self.launch()


class Execute:
    """executes function"""

    def translate(self, data: TranslateData, temp_file=""):
        """translates string (multiple replace)"""

        if temp_file != "":
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

        translate_data_temp = {
            "$LINGFO_ARGS": args,
        }

        translate_utils = {
            "$LINGFO_SEMICOLON": ";",
            "$LINGFO_FUNCTION": data.call_function,
        }

        class_call_translate = {}

        if data.is_class:
            # prepare translate data
            class_call_translate = {
                "$LINGFO_RANDOM": "".join(choices(ascii_lowercase, k=3)),
                "$LINGFO_CLASS": self.class_name,
            }

            class_call_translate = {**class_call_translate, **translate_utils}

        translate_data = {
            "$LINGFO_IMPORT": data.import_syntax.replace("[file-name]", data.file_name),
            "$LINGFO_NEWLINE": "\n",
            "$LINGFO_ARGS": "",
        }

        translate_data = {**translate_data, **translate_utils}

        if data.is_class:
            # translate it
            translate_data = {**class_call_translate, **translate_data}
            function_class = config["launch"]["class_call_syntax"]

            for i, j in {**translate_data, **translate_data_temp}.items():
                function_class = function_class.replace(i, j)

            # and then combine translate data and output of this translate process
            new_translate_data = {"$LINGFO_FUNCTION": function_class}
            translate_data = {**translate_data, **new_translate_data}

        for i, j in {**translate_data, **translate_data_temp}.items():
            self.temp_file = self.temp_file.replace(i, j)

        return self.temp_file

    def __init__(
        self, file, uuid, is_class, class_name, *args, use_multiple_execute=False
    ) -> None:
        self.temp_file = ""
        self.init_args = INIT_ARGS
        self.temp_file = TEMP_FILE
        self.is_class = is_class
        self.class_name = class_name

        if use_multiple_execute is True:
            return

        # get from what function was this called
        if lingfocache.CUSTOM_TEMP_FILE is None:
            call_function = inspect.stack()[1].function
        else:
            call_function = lingfocache.CUSTOM_TEMP_FILE

        call_function = inspect.stack()[1].function
        verbose_print(
            f"[bold green]lingfo[/bold green]   finding function {call_function}"
        )

        self.init_args = re.sub("[()]", "", rf"{args}".replace(",", ""))
        if config.getboolean("main", "use_templates") is True:
            import_syntax = lingfocache.TEMPLATE_IMPORT_SYNTAX
        else:
            import_syntax = launch_config["import_syntax"]

        if config.getboolean("main", "use_templates") is True:
            self.temp_file = lingfocache.TEMPLATE_TEMP_FILE
        else:
            self.temp_file = config["temp_file"]["temp_file"]

        if ONE_COMPILE:
            # if () is in temp file remove it
            delimiter = "LINGFO_FUNCTION"

            index = self.temp_file.find(delimiter)
            after = self.temp_file[index + len(delimiter) :]

            # TODO: cleanup!
            after = (
                after.replace("$LINGFO_ARGS", "")
                .replace("$LINGFO_SEMICOLON", "")
                .replace("}", "")
            )

            if after == "()":
                self.temp_file = self.temp_file.replace("($LINGFO_ARGS)", "")

        lib_path_first = config["main"]["lib_path"].split("/")[0]
        new_file = file.replace(f"{lib_path_first}/", "")
        data = TranslateData(
            import_syntax, new_file, call_function, self.init_args, self.is_class
        )
        self.translate(data)

        if config.getboolean("launch", "multiple_functions") is True:
            multiple_execute = MultipleExecute()
            multiple_execute.save("function", call_function, file, self.init_args)
        else:
            self.function(uuid)

    def function(self, uuid, output=None):
        """runs function from another language"""

        path = main_config["lib_path"].split("/")[0]

        # if lingfocache.LAST_EXECUTED_CODE == self.temp_file and ONE_COMPILE is False:
        #     system(f"./{path}/out")
        #     return TODO: fix

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
            verbose_print("[bold green]lingfo[/bold green]   executing function ")
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
                f"LAST_EXECUTED_CODE = {lingfocache.LAST_EXECUTED_CODE}",
                f'LAST_EXECUTED_CODE = """{TEMP_FILE}"""',
            )

        # we should skip it if using one (time) compile
        if ONE_COMPILE is False:
            execute_prelaunch()

        print(uuid)
        # remove temp file
        remove(f"{path}/temp.{temp_extension}")
        subprocess.call([f"./{path}/out", uuid], shell=False)
