import configparser

from .stores import ONE_COMPILE

config = configparser.ConfigParser()
config.read("sushi.conf")


class OneCompile:
    def __init__(self) -> None:
        if ONE_COMPILE == False:
            return

        path = config["main"]["lib_path"].split("/")[0]
        temp_extension = config["temp_file"]["extension"]

        with open(
            file=f"{path}/temp.{temp_extension}", mode="w", encoding="UTF-8"
        ) as f:
            f.write("")
        f.close()
