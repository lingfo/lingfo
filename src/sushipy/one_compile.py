"""one compile"""

import configparser
import uuid
from contextlib import suppress
from os.path import isfile

from .cache.main import Cache

config = configparser.ConfigParser()
config.read("sushi.conf")

# pylint: disable=import-error
if isfile("sushicache.py"):
    import sushicache

    DATA = sushicache.INDEXED_FUNCTIONS
# pylint: enable=import-error


class OneCompile:
    """one compile"""

    def setup(self) -> None:
        """setup onecompile"""

        # TODO: cleanup
        if_data = self._extract_if()
        data = [{"uuid": str(uuid.uuid4()), "name": DATA[0]["name"]}]
        out = self._parse_if(if_data["if"], data[0]["uuid"], data[0]["name"])

        if len(DATA) > 1:
            for x in range(len(DATA)):
                with suppress(IndexError):
                    out += self._parse_if(
                        if_data["else"], str(uuid.uuid4()), DATA[x + 1]["name"]
                    )

        Cache.update(
            Cache,
            f'CUSTOM_TEMP_FILE = """{sushicache.CUSTOM_TEMP_FILE}"""',
            f'CUSTOM_TEMP_FILE = """{out}"""',
        )

        return data

    def _extract_if(self):
        # extracts if statements
        launch = config["launch"]["if_statement"]
        else_start = "$SUSHI_ELSE_START"

        split_string = launch.split(else_start)

        return {"if": split_string[0], "else": split_string[1]}

    def _parse_if(self, data, uuid_data, code):
        translate_date = {
            "$SUSHI_ARG_NUM": "1",
            "$SUSHI_SEMICOLON": ";",
            "$SUSHI_UUID": uuid_data,
            "$SUSHI_CODE": code,
        }

        for i, j in translate_date.items():
            data = data.replace(i, j)

        return data
