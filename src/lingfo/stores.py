"""
here lingfo stores all variables that are used in multiple files
"""

import configparser

config = configparser.ConfigParser()
config.read("lingfo.conf")

MULTIPLE_FILES = False
ONE_COMPILE = False


split_path = config["main"]["lib_path"].split("/")
if split_path[-1] == "*":
    MULTIPLE_FILES = True

try:
    ONE_COMPILE = config.getboolean("launch", "one_compile")
except configparser.NoOptionError:
    ONE_COMPILE = False
