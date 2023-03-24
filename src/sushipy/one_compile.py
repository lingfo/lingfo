"""one compile"""

import configparser
import uuid
from contextlib import suppress
from os.path import isfile

from .cache.main import Cache
from .stores import ONE_COMPILE

config = configparser.ConfigParser()
config.read("sushi.conf")

# pylint: disable=import-error
if isfile("sushicache.py"):
    import sushicache
# pylint: enable=import-error

DATA = sushicache.INDEXED_FUNCTIONS


class OneCompile:
    """one compile"""

    def __init__(self) -> None:
        if not ONE_COMPILE:
            return

        # TODO: cleanup
        if_data = self._extract_if()
        out = self._parse_if(if_data["if"], str(uuid.uuid4()), DATA[0]["name"])

        for x in range(len(DATA)):
            with suppress(IndexError):
                out += self._parse_if(
                    if_data["else"], str(uuid.uuid4()), DATA[x + 1]["name"]
                )

        Cache.update(
            Cache,
            f"CUSTOM_TEMP_FILE = {sushicache.CUSTOM_TEMP_FILE}",
            f'CUSTOM_TEMP_FILE = """{out}"""',
        )

    def _extract_if(self):
        # extracts if statements
        launch = config["launch"]["if_statement"]
        else_start = "$SUSHI_ELSE_START"

        split_string = launch.split(else_start)

        return {"if": split_string[0], "else": split_string[1]}

    def _parse_if(self, data, uuid, code):
        translate_date = {
            "$SUSHI_ARG": "arg",
            "$SUSHI_UUID": uuid,
            "$SUSHI_CODE": code,
        }

        for i, j in translate_date.items():
            data = data.replace(i, j)

        return data
