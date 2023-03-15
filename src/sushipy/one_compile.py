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

        function_uuid = []

        with open(
            file=f"{path}/temp.{temp_extension}", mode="w", encoding="UTF-8"
        ) as f:
            for x in DATA:
                # generate uuids for functions
                function_uuid.append({"name": x["name"], "uuid": str(uuid.uuid4())})

            # now create if statements

        f.close()

        # print(function_uuid)
        self._extract_if()

    def _extract_if(self):
        # extracts if statements
        launch = config["launch"]["if_statement"]
        else_start = "$SUSHI_ELSE_START"

        split_string = launch.split(else_start)

        return {"if": split_string[0], "else": split_string[1]}
