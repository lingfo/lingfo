"""
a little tool for sushi to help manage variables
"""

import os
from .verbose_print import verbose_print


class SushiVariable:
    """sushi variable"""

    def update(self, new_data: str):
        """updates variable"""

        with open(".sushi/var_data.txt", "w", encoding="UTF-8") as f:
            f.write(f"{self.variable_name}:{new_data}")

    def read(self):
        """reads from variable"""

        try:
            with open(".sushi/var_data.txt", "r", encoding="UTF-8") as f:
                lines = f.readlines()

                for x in lines:
                    if self.variable_name in x:
                        # found variable
                        split = x.split(":")
                        variable_content = split[1]

                        return variable_content
        except FileNotFoundError:
            verbose_print(
                "[yellow bold]sushi[/yellow bold]   warning! trying to read variable while\
.sushi/var_data.txt was not created! returning empty string"
            )

            return ""
        return ""

    def __init__(self, variable_name, base_data) -> None:
        self.variable_name = variable_name

        if base_data != "":
            self.update(base_data)

    def __del__(self):
        # remove sushi var data

        os.remove(".sushi/var_data.txt")
