"""verbose print"""

import configparser

from rich import print as rich_print

# TODO: maybe move to stores.py

config = configparser.ConfigParser()
config.read("sushi.conf")

verbose_flag = config["launch"].getboolean("verbose", fallback=False)


def verbose_print(message: str):
    """
    Prints a verbose message using rich library if the 'verbose' flag is set to True.

    Args:
        message (str): The message to be printed.
        verbose (bool): A flag to determine if the message should be printed or not.

    Example:
        verbose_print("This is a verbose message", verbose=True)
    """
    if verbose_flag:
        rich_print(message)
