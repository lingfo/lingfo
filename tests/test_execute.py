# pylint: disable=missing-module-docstring, missing-function-docstring

import configparser
import os
import shutil
import subprocess

import pytest


def modify_config():
    config = configparser.ConfigParser()
    config.read("sushi.conf")

    # disable safe_mode
    config["main"]["safe_mode"] = "no"

    # save new config
    with open("sushi.conf", "w", encoding="utf-8") as f:
        config.write(f)


@pytest.fixture(scope="session", autouse=True)
def pytest_init():
    # copy example so we have already built sushi app for testing
    noarg_path = os.path.abspath("../examples/cpp")
    arg_path = os.path.abspath("../examples/arg-cpp")

    shutil.copytree(noarg_path, "noarg-temp/")
    shutil.copytree(arg_path, "arg-temp/")

    yield  # run all tests

    # Cleanup temporary directories after testing
    shutil.rmtree("noarg-temp/")
    shutil.rmtree("arg-temp/")


class TestExecute:
    """
    Tests Execute() using example apps
    """

    def run_example(self, directory):
        """Helper function to run example app and return the result."""
        os.chdir(directory)
        modify_config()

        result = subprocess.run(
            ["python3", "app.py"], capture_output=True, text=True, check=True
        )
        result = result.stdout.split("\n")

        print(result)
        os.chdir("../")

        return result

    def test_noarg(self):
        result = self.run_example("noarg-temp/")
        assert result[3] == "Hello from sushi!"

    def test_arg(self):
        result = self.run_example("arg-temp/")
        assert result[3] == "You provided 1"
