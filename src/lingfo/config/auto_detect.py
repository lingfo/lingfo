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
            depth=1
        )

        # and build library for tree-sitter
        Language.build_library(
            file_path + f"build/{language}.so", [file_path + "source/"]
        )

        Cache.update(
            Cache, "TREE_SITTER_CONFIGURED = False", "TREE_SITTER_CONFIGURED = True"
        )

    def __init__(self, language: str, content: str) -> None:
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

        for node in tree.root_node.children:
            with suppress(IndexError):
                extract = node.children[1]

                # get on what line it is indexing
                lines = str(extract.end_point)
                lines = (
                    lines.replace("(", "").replace(")", "").split(",", maxsplit=1)[0]
                )
                lines = int(lines)

                if node.type == 'class_specifier':
                    for x in node.children:
                        print(x.text)
                        
                # grab all functions and variables
                if node.type == "function_definition":
                    output.append({"type": "function", "data": extract.text})
                elif node.type == "declaration" and "=" in str(extract.text):
                    output.append({"type": "variable", "data": extract.text})

        return output
