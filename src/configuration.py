"""
    This is a helper file to read the configuration file and manage the test plan
"""

from glob import glob
import json
import logging
import os
import re

LOGGER = logging.getLogger(__name__)

syntax = [
    lambda entry: glob("data/tests/**/"+entry, recursive=True) if entry.lower()[-3:] == ".py" else [],
    lambda entry: glob("data/tests/**/"+entry+".py", recursive=True),
    lambda entry: glob("data/tests/**/"+entry+"/**/*.py", recursive=True),
    lambda entry: glob(entry)
]


def merge_test_plan(config_default, config_custom):
    """Merge two test plans configuration dictionaries

    Args:
        config_default (dict): containing the standard values
        config_custom (dict): containing values overwriting the default

    Returns:
        dict: merged test plan configration
    """
    config = {}
    config["tests"] = merge_tests(config_default.setdefault("tests", []), config_custom.setdefault("tests", []))
    config["configuration"] = merge_configuration(config_default.setdefault("configuration", {}), config_custom.setdefault("configuration", {}))
    return config


def merge_tests(default, custom):
    """Merte two lists

    Args:
        default (list): default
        custom (list): additional

    Returns:
        list: merged list
    """
    return default + custom


def merge_configuration(default, custom):
    """Merge two configuration dictionaries recursively

    Args:
        default (dict): containing the standard values
        custom (dict): containing values overwriting the default

    Returns:
        dict: merged configuration
    """
    if type(default) is not dict:
        return custom
    common_keys = set(default).intersection(custom)
    new_keys = set(custom).difference(common_keys)
    for k in common_keys:
        default[k] = merge_configuration(default[k], custom[k])
    for k in new_keys:
        default[k] = custom[k]
    return default


def load_json_file(path):
    """load json object from a file and fill environment variable placeholder

    Args:
        path (str): path to json file

    Returns:
        dict: dictionary representing the json content
    """
    assert os.path.exists(os.path.dirname(path)), "file does not exists"
    config = {}
    with open(path) as config_file:
        json_str_replaced = insert_environment_variables(config_file.read())
        config = json.loads(json_str_replaced)
    return config


def load_json_str(json_str):
    """load json object from string and fill environment variable placeholder

    Args:
        json_str (str): json string

    Returns:
        dict: dictionary representing the json content
    """
    json_str_replaced = insert_environment_variables(json_str)
    config = json.loads(json_str_replaced)
    return config


def insert_environment_variables(json_str):
    """replace placeholders with content of environment variables

    Args:
        json_str (str): json string

    Returns:
        str: filled json string
    """
    regex = re.compile(r'\$(\w+|\{[^}]*\})')

    def os_expandvar(match):
        v = match.group(1)
        if v.startswith('{') and v.endswith('}'):
            v = v[1:-1]
        return json.dumps(os.environ.get(v, ''))[1:-1]
    json_str_replaced = regex.sub(os_expandvar, json_str)
    return json_str_replaced


class Test_Plan:
    tests = []
    configuration = None

    def __init__(self, path=None, configuration=None):
        device_config = {
            "tests": [],
            "configuration": {}
        }
        if configuration is not None:
            if type(configuration) is Test_Plan:
                device_config["tests"] = configuration.get_testfiles()
                device_config["configuration"] = configuration.get_configuration()
            if type(configuration) is Configuration:
                device_config["tests"] = []
                device_config["configuration"] = configuration.get_configuration()
        if path is not None:
            device_config = merge_test_plan(device_config, load_json_file(path))
        if configuration is not None and type(configuration) is str:
            device_config = merge_test_plan(device_config, load_json_str(configuration))
        self.load_test_plan(device_config)

    def merge(self, configuration):
        config = self.get_test_plan()
        if type(configuration) is Test_Plan:
            config = merge_test_plan(config, configuration.get_test_plan())
        elif type(configuration) is dict:
            config = merge_test_plan(config, configuration)
        elif os.path.exists(os.path.dirname(configuration)):
            config = merge_test_plan(config, load_json_file(configuration))
        else:
            assert False, "the argument provided to merg a test plan must be a file name, a Test_Plan or an Object representing the test plan JSON"
        self.load_test_plan(config)

    def load_test_plan(self, config):
        assert self.check_test_plan(config), "Test Plan Configuration File can not be understood, see log"

        self.tests = config.setdefault("tests", [])
        self.configuration = Configuration(configuration=config.setdefault("configuration", {}))

    def check_syntax(self, tests):
        def syntax_test(entry): return len(sum([syntaxi(entry) for syntaxi in syntax], [])) > 0
        syntax_tests = list(filter(None, [entry if not syntax_test(entry) else "" for entry in tests]))
        return syntax_tests

    def check_test_plan(self, config):
        if type(config) is not dict:
            LOGGER.error("Test Plan was provided but could not be read")
            return False
        if "configuration" in config:
            if type(config["configuration"]) is not dict:
                LOGGER.error("Configration was provided but could not be read")
                return False
        if "tests" in config:
            if type(config["tests"]) is not list:
                LOGGER.error("A list of test cases was provided but could not be read")
                return False
            tests = config.setdefault("tests", [])
            syntax_fail_test = self.check_syntax(tests)
            if len(syntax_fail_test) == 0:
                LOGGER.info("The list of test cases is plausible and the tests were found")
            else:
                LOGGER.warn(f"The following test cases could not be found in the file system:\n{syntax_fail_test}")
        else:
            LOGGER.info("No list of test cases was specified in the custom configuration. Therefore it will use all detectable test cases.")
        return True

    def is_in_scope(self, path):
        for test in self.get_testfiles():
            try:
                if os.path.commonpath([os.path.abspath(path)]) == os.path.commonpath([os.path.abspath(path), os.path.abspath(test)]):
                    return True
                # The upper function already returns True when the file is the same
                # if os.path.samefile(path, test):
                #    return True
            except:
                pass
        return False

    def get_testfiles(self):
        testfiles = sum([sum([syntaxi(entry) for syntaxi in syntax], []) for entry in self.tests], [])
        return testfiles

    def get_configuration(self):
        return self.configuration.get_configuration()

    def get_test_plan(self):
        config = {
            "tests": self.tests,
            "configuration": self.configuration.get_configuration()
        }
        return config


class Configuration:
    configuration = {}

    def __init__(self, path=None, configuration=None):
        config = {}
        if configuration is not None:
            if type(configuration) is Test_Plan:
                config = configuration.get_configuration()
            elif type(configuration) is str:
                config = load_json_str(configuration)
            else:
                config = configuration
        elif path is not None:
            config = load_json_file(path)

        self.load_config(config)

    def merge(self, configuration):
        config_new = self.configuration
        if type(configuration) is Configuration:
            config_new = merge_configuration(config_new, configuration.get_configuration())
        elif type(configuration) is Test_Plan:
            config_new = merge_configuration(config_new, configuration.get_configuration())
        elif type(configuration) is dict:
            config_new = merge_configuration(config_new, configuration)
        elif os.path.exists(os.path.dirname(configuration)):
            config_new = merge_configuration(config_new, load_json_file(configuration))
        else:
            assert False, "the argument provided to merg a test plan must be a file name, a Test_Plan or an Object representing the test plan JSON"
        self.load_config(config_new)

    def load_config(self, config):
        assert self.check_configuration(config), "Configuration File can not be understood, see log"

        self.configuration = config

    def check_configuration(self, config):
        if type(config) is not dict:
            LOGGER.error("Configration was provided but could not be read")
            return False
        return True

    def get_configuration(self, test=None):
        if test is not None:
            return {**self.configuration.get("global", {}), **self.configuration.get(test, {})}
        return self.configuration

    def customize_config(self, key, value, test="global"):
        self.configuration.setdefault(test, {})[key] = value
