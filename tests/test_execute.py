# pylint: disable=missing-module-docstring, missing-function-docstring

import os
import shutil
import subprocess

import pytest


@pytest.fixture(scope="session", autouse=True)
def pytest_init():
    # copy example so we have already built sushi app for testing
    noarg_path = os.path.abspath("../examples/cpp")
    arg_path = os.path.abspath("../examples/arg-cpp")

    shutil.copytree(noarg_path, "noarg-temp/")
    shutil.copytree(arg_path, "arg-temp/")

    yield  # run all tests

    # cleanup
    shutil.rmtree("noarg-temp/")
    shutil.rmtree("arg-temp/")


class TestExecute:
    """
    tests Execute() using a example app
    """

    def test_noarg(self):
        # use example
        os.chdir("noarg-temp/")

        result = subprocess.run(
            ["python3", "app.py"], capture_output=True, text=True, check=False
        )
        result = result.stdout.split("\n")

        print(result)
        os.chdir("../")

        assert result[1] == "Hello from sushi!"

    def test_arg(self):
        # use example
        os.chdir("arg-temp/")

        result = subprocess.run(
            ["python3", "app.py"], capture_output=True, text=True, check=False
        )
        result = result.stdout.split("\n")

        print(result)
        os.chdir("../")

        assert result[1] == "You provided 1"
