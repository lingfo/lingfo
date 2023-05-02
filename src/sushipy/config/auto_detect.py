"""
auto detect using tree-sitter
"""

import configparser
from contextlib import suppress
import os
from os.path import isfile

from git import Repo
from rich import print as rich_print
from tree_sitter import Language, Parser

from ..cache.main import Cache

# pylint: disable=import-error
if isfile("sushicache.py"):
    import sushicache
# pylint: enable=import-error

config = configparser.ConfigParser()
config.read("sushi.conf")


class EditVariable:
    """edit variable"""

    def extract_arg(self):
        """extract get argument stuff that is used for
        if statements one time compile"""

        # get if statement
        if config.getboolean("main", "use_templates") == True:
            if_statement = sushicache.TEMPLATE_IF_STATEMENT
        else:
            if_statement = config["launch"]["if_statement"]
        if_statement = if_statement.split("$SUSHI_ARG_NUM")

        # remove text from if statement so we will get only argument call
        first = if_statement[0].replace("if", "")
        second = if_statement[1].split("==")[0]

        if "(" in first:
            first = first.replace("(", "")

        # connect two parts TODO: is every language using array for that?
        if_statement = first + str(0) + second

        return if_statement


class TSDetect:
    """detect using TreeSitter"""

    def setup(self, file_path, language):
        """setup tree sitter"""

        rich_print(
            "[bold green]sushi[/bold green]    configuring tree-sitter for your language"
        )

        if not os.path.exists(".sushi"):
            os.makedirs(".sushi")

        # first, download parser for selected language
        Repo.clone_from(
            f"https://github.com/tree-sitter/tree-sitter-{language}",
            file_path + "source/",
        )

        # and build library for tree-sitter
        Language.build_library(
            file_path + f"build/{language}.so", [file_path + "source/"]
        )

        Cache.update(
            Cache, "TREE_SITTER_CONFIGURED = False", "TREE_SITTER_CONFIGURED = True"
        )

    def __init__(self, language: str, content: str) -> None:
        file_path = f".sushi/tree-sitter-{language}/"

        try:
            # setup tree sitter
            if sushicache.TREE_SITTER_CONFIGURED is False:
                self.setup(file_path, language)
        except NameError:
            self.setup(file_path, language)

        tree_lang = Language(file_path + f"build/{language}.so", language)

        # create new parser
        parser = Parser()
        parser.set_language(tree_lang)

        self.tree = parser.parse(
            bytes(
                content,
                "utf8",
            )
        )

        self.parse_tree()

    def parse_tree(self):
        """parse tree"""

        tree = self.tree
        output = []

        for node in tree.root_node.children:
            with suppress(IndexError):
                extract = node.children[1]

                # get on what line it is indexing
                lines = str(extract.end_point)
                lines = (
                    lines.replace("(", "").replace(")", "").split(",", maxsplit=1)[0]
                )
                lines = int(lines) + 1

                # grab all functions and variables
                if node.type == "function_definition":
                    output.append({"type": "function", "data": extract.text})
                elif node.type == "declaration" and "=" in str(extract.text):
                    output.append({"type": "variable", "data": extract.text})

                e = EditVariable()
                e.extract_arg()
        return output
