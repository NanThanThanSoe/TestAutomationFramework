"""
    This is a headless prototype to execute pytest test cases with a custom configuration file
"""

import json
from configuration import Test_Plan
import pytest
import os

def run():
    boxip = os.environ.get("BOX_IP", "10.13.201.18")
    print(f"Using Box IP: {boxip}")
    config = Test_Plan("data/configuration/nan.json")

    config.configuration.customize_config("rhost", boxip)

    pytest.main(["--html", "logs/output.html", "--self-contained-html"] + ["--junitxml", "logs/output.junit"] +
                ["--configuration", json.dumps(config.get_configuration())] + config.get_testfiles())


if __name__ == "__main__":
    run()
