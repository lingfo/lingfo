# pylint: disable=missing-module-docstring, missing-function-docstring

import os
import shutil
import subprocess


class TestExecute:
    """
    tests Execute() using a example app
    """

    def cleanup(self):
        os.chdir("../")
        shutil.rmtree("temp/")

    def test_noarg(self):
        # copy example so we have already built sushi app for testing
        examples_path = os.path.abspath("../examples/cpp")
        shutil.copytree(examples_path, "temp/")

        # now use this example
        os.chdir("temp/")

        result = subprocess.run(
            ["python", "app.py"], capture_output=True, text=True, check=False
        )
        result = result.stdout.split("\n")

        print(result)

        self.cleanup()
        if result[1] == "Hello from sushi!":
            assert True
        else:
            assert False
