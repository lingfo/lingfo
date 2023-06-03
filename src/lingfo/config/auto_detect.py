"""
auto detect using tree-sitter
"""

import configparser
from contextlib import suppress
import os
from os.path import isfile

from git import Repo
from tree_sitter import Language, Parser
from ..utils.rich_print import rich_print

from ..cache.main import Cache

# pylint: disable=import-error
if isfile("lingfocache.py"):
    import lingfocache
# pylint: enable=import-error

config = configparser.ConfigParser()
config.read("lingfo.conf")


class TSDetect:
    """detect using TreeSitter"""

    def setup(self, file_path, language):
        """setup tree sitter"""

        rich_print(
            "[bold green]lingfo[/bold green]    configuring tree-sitter for your language"
        )

        if not os.path.exists(".lingfo"):
            os.makedirs(".lingfo")

        # first, download parser for selected language
        Repo.clone_from(
            f"https://github.com/tree-sitter/tree-sitter-{language}",
            file_path + "source/",
            depth=1,
        )

        # and build library for tree-sitter
        Language.build_library(
            file_path + f"build/{language}.so", [file_path + "source/"]
        )

        Cache.update(
            Cache, "TREE_SITTER_CONFIGURED = False", "TREE_SITTER_CONFIGURED = True"
        )

    def __init__(
        self, language: str, content: str, relaunch: bool = False, class_name: str = ""
    ) -> None:
        self.language = language
        self.relaunch = relaunch
        self.class_name = class_name

        file_path = f".lingfo/tree-sitter-{language}/"

        try:
            # setup tree sitter
            if lingfocache.TREE_SITTER_CONFIGURED is False:
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
        self.new_output = []  # output used for class content parsing

        def save(data):
            if self.relaunch is False:
                output.append(data | {"from": "file"})
            else:
                output.append(data | {"from": "class", "class_name": self.class_name})

        for node in tree.root_node.children:
            with suppress(IndexError):
                extract = node.children[1]

                # get on what line it is indexing
                lines = str(extract.end_point)
                lines = (
                    lines.replace("(", "").replace(")", "").split(",", maxsplit=1)[0]
                )
                lines = int(lines)

                # grab all functions and variables
                if node.type == "function_definition":
                    save({"type": "function", "data": extract.text})
                elif node.type == "declaration" and "=" in str(extract.text):
                    save({"type": "variable", "data": extract.text})

                if node.type == "class_specifier" and self.relaunch is False:
                    class_content = node.children[2].text
                    self.class_name = extract.text.decode()

                    # remove unnecessary characters
                    class_content = class_content.decode()

                    # for C/C++ and other languages that use similar class structure
                    class_content = class_content.replace("public:", "").replace(
                        "private:", ""
                    )
                    class_content = class_content.split("\n", 1)[
                        1
                    ]  # remove first line from string

                    # relaunch to parse content inside class
                    new_detect = TSDetect(
                        self.language, class_content, True, self.class_name
                    )
                    self.new_output += new_detect.parse_tree()
        if len(self.new_output) == 0:
            # class wasnt found, so there isnt any new_output
            return output
        return [output, *self.new_output]
