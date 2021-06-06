from serialtestutil import rs232_profiles, ibis_config


# Implement the run profile markers/selectors used by rs232-test.py.
def pytest_addoption(parser):
    """Adds various options for test profile selection or extra test parameters."""
    parser.addoption(
        "-P", "--rs232-profile",
        action="store",
        metavar="PROFILE",
        default=rs232_profiles.DEFAULT_PROFILE_NAME,
        choices=rs232_profiles.get_available_profiles(),
        help="Run RS232 tests matching the profile %(metavar)s. Possibles values: %(choices)s. Default value: %(default)s",
    )

    parser.addoption(
        "-S", "--ibis-max-data-size",
        action="store",
        metavar="MAX_SIZE",
        type=int,
        default=300,
        help="Maximum data size for IBIS send/receive tests. Default: %(default)s"
    )

    parser.addoption(
        "-C", "--ibis-endurance-cycles",
        action="store",
        metavar="CYCLES",
        type=int,
        default=100,
        help="Number of cycles for IBIS endurance testing. Default: %(default)s"
    )


def pytest_configure(config):
    """Selects the active test profile based on the value of the -P option and sets various global variables used in other tests."""
    if config.option.rs232_profile:
        rs232_profiles.set_selected_profile(config.option.rs232_profile)

    if config.option.ibis_max_data_size:
        ibis_config.max_data_size = config.option.ibis_max_data_size

    if config.option.ibis_endurance_cycles:
        ibis_config.endurance_cycle_count = config.option.ibis_endurance_cycles