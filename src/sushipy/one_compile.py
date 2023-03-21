"""one compile"""

import configparser
import uuid
from os.path import isfile

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

        path = config["main"]["lib_path"].split("/")[0]
        temp_extension = config["temp_file"]["extension"]

        # TODO: cleanup
        with open(
            file=f"{path}/temp.{temp_extension}", mode="w", encoding="UTF-8"
        ) as f:
            if_data = self._extract_if()
            out = self._parse_if(if_data["if"], str(uuid.uuid4()))

            for x in DATA:
                out += self._parse_if(if_data["else"], str(uuid.uuid4()))
            print(out)

        f.close()

        # print(function_uuid)

    def _extract_if(self):
        # extracts if statements
        launch = config["launch"]["if_statement"]
        else_start = "$SUSHI_ELSE_START"

        split_string = launch.split(else_start)

        return {"if": split_string[0], "else": split_string[1]}

    def _parse_if(self, data, uuid):
        translate_date = {
            "$SUSHI_ARG": "arg",
            "$SUSHI_UUID": uuid,
            "$SUSHI_CODE": "code",
        }

        for i, j in translate_date.items():
            data = data.replace(i, j)

        return data
