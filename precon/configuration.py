import pytest
import logging
import glob
import json
import re

from src.configuration import Configuration, Test_Plan

LOGGER = logging.getLogger(__name__)


def pytest_addoption(parser):
    """
    Define command line parameters
    """
    parser.addoption("--configuration", action="store", default=None, help="")
    parser.addoption("--configuration_file", action="store", default=None, help="")

def pytest_configure(config):
    """Create the test plan from the default configuration and configuration file or json provided via command line
    It will store the test_plan inside the config for further usage.

    Args:
        config (Config): The pytest config object.
    """
    # load default global configuration (test specific config will not be loaded yet!)
    config_default = config_default_load()
    print(f"Loading default configuration {replace_password_json_value(json.dumps(config_default.get_configuration()))}")
    test_plan = Test_Plan()
    if config.getoption("--configuration_file") is not None:
        config_custom_file = Test_Plan(path=config.getoption("--configuration_file"))
        print(f"Loading custom configuration file {replace_password_json_value(json.dumps(config_custom_file.get_configuration()))}")
        test_plan.merge(config_custom_file)
    if config.getoption("--configuration") is not None:
        config_custom_json = Test_Plan(configuration=config.getoption("--configuration"))
        print(f"Loading custom configuration {replace_password_json_value(json.dumps(config_custom_json.get_configuration()))}")
        test_plan.merge(config_custom_json)
    print(f"Merged custom configuration {replace_password_json_value(json.dumps(test_plan.get_configuration()))}")

    config.config_default = config_default
    config.test_plan = test_plan

def pytest_ignore_collect(path, config):
    """Read the test plan and only collect test cases in scope of the test plan.
    Ignore nothing if the test plan has no test specified.

    Args:
        path (py._path.local.LocalPath): The path to analyze.
        config (Config): The pytest config object.

    Returns:
        bool: Return True to prevent considering this path for collection.
    """
    if len(config.test_plan.get_testfiles()) == 0: return False
    return not config.test_plan.is_in_scope(path)

@pytest.fixture(scope="module")
def configuration(request):
    """Provides the test configuration for a specific test file. Merged standard and custom configuration.

    Args:
        request (FixtureRequest): The request fixture is a special fixture providing information of the requesting test function.

    Returns:
        dict: configuration represented as key value pairs
    """
    # load global default and test-specific configuration
    config = config_default_load(request.module.__name__)
    
    # merge the global default and test-specific configuration with the customized configuration
    config.merge(request.config.test_plan)

    # extract the combined global and test-specific configuration
    configuration_merged_global_and_test = config.get_configuration(request.module.__name__)

    configuration_string = json.dumps(configuration_merged_global_and_test)
    LOGGER.info(f"Merged configuration {replace_password_json_value(configuration_string)}")
    
    return configuration_merged_global_and_test

@pytest.fixture(scope="session")
def configuration_default(request):
    """Provides the default global test configuration. Merged standard and user-defined configuration
    Disregard test specific configuration.

    Args:
        request (FixtureRequest): The request fixture is a special fixture providing information of the requesting test function.

    Returns:
        dict: configuration represented as key value pairs
    """
    # load global default configuration
    config = config_default_load()
    
    # merge the global default with the customized configuration
    config.merge(request.config.test_plan)

    # extract the combined global configuration
    configuration_merged = config.get_configuration("global")

    configuration_string = json.dumps(configuration_merged)
    LOGGER.info(f"Merged default configuration {replace_password_json_value(configuration_string)}")
    
    return configuration_merged

@pytest.fixture(scope="session")
def configuration_all(request):
    """Provides nested test configuration for all tests. Merged standard, test-specific and user-defined configuration

    Args:
        request (FixtureRequest): The request fixture is a special fixture providing information of the requesting test function.

    Returns:
        dict: configuration represented as key value pairs
    """
    # load default merged with test specific configuration
    config = config_default_load("*")
    
    # merge the default and test specific with the customized configuration
    config.merge(request.config.test_plan)

    configuration_merged = config.get_configuration()

    configuration_string = json.dumps(configuration_merged)
    LOGGER.info(f"Nested configuration {replace_password_json_value(configuration_string)}")
    
    return configuration_merged

def replace_password_json_value(json):
    """hide sensitive information in json strings.
    Replace each value whose key contains the substring 'password' with ***

    Args:
        json (str): presumably with confidential information

    Returns:
        str: masked json
    """
    json_string_safe = re.sub(r"(\"([^\"]*(password)[^\"]*)\": )([^,}]*)(,|})", lambda matchobj: f"{matchobj[1]}\"********\"{matchobj[5]}", json)
    return json_string_safe

def config_default_load(testid=None):
    """read and merge global and test specific default configuration files for a specific test

    Args:
        testid (string, optional): test file name. Defaults to None.

    Returns:
        Configuration: default configruation for specific test
    """

    config = Configuration()
    config_global = Configuration(path='data/default.json')
    config.merge({"global": config_global.get_configuration()})

    if testid is not None:
        for f_name in glob.glob('data/tests/**/'+(testid if testid else '*')+'.json', recursive=True):
            config_test = Configuration(path=f_name)
            key = re.search(r"([\w\d\-.]+)\.json", f_name)[1]
            config.merge({f"{key}": config_test.get_configuration()})

    return config
