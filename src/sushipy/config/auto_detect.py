"""
auto detect using tree-sitter
"""

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
            extract = node.children[1]

            # grab all functions and variables
            if node.type == "function_definition":
                output.append(extract.text)
            elif node.type == "declaration" and "=" in str(extract.text):
                print(extract.text)

        return output
