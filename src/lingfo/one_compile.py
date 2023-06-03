"""one compile"""

import configparser
import uuid
from contextlib import suppress
from os.path import isfile

from .utils.rich_print import rich_print

from .cache.main import Cache

config = configparser.ConfigParser()
config.read("lingfo.conf")

# pylint: disable=import-error
if isfile("lingfocache.py"):
    import lingfocache

# pylint: enable=import-error


class OneCompile:
    """one compile"""

    def setup(self) -> None:
        """setup onecompile"""

        cache_data = lingfocache.INDEXED_FUNCTIONS

        # TODO: cleanup
        if_data = self._extract_if()
        data = [{"uuid": str(uuid.uuid4()), "name": cache_data[0]["name"]}]
        out = self._parse_if(if_data["if"], data[0]["uuid"], data[0]["name"])

        if len(cache_data) > 1:
            for x in range(len(cache_data)):
                with suppress(IndexError):
                    out += self._parse_if(
                        if_data["else"], str(uuid.uuid4()), cache_data[x + 1]["name"]
                    )

        Cache.update(
            Cache,
            f'CUSTOM_TEMP_FILE = """{lingfocache.CUSTOM_TEMP_FILE}"""',
            f'CUSTOM_TEMP_FILE = """{out}"""',
        )

        return data

    def _extract_if(self):
        # extracts if statements

        launch = config["launch"]["if_statement"]
        if config.getboolean("main", "use_templates") is True:
            launch = lingfocache.TEMPLATE_IF_STATEMENT
        else_start = "$LINGFO_ELSE_START"

        split_string = launch.split(else_start)

        return {"if": split_string[0], "else": split_string[1]}

    def _parse_if(self, data, uuid_data, code):
        translate_data = {
            "$LINGFO_ARG_NUM": "1",
            "$LINGFO_SEMICOLON": ";",
            "$LINGFO_UUID": uuid_data,
            "$LINGFO_CODE": code,
        }

        for i, j in translate_data.items():
            data = data.replace(i, j)

        return data

    def __init__(self) -> None:
        rich_print("[bold red]lingfo[/bold red]   one compile is still experimental")

        # TODO: implement other cache system
        try:
            if lingfocache.ONE_COMPILE_CONFIGURED is False:
                self.setup()
        except NameError:
            return
