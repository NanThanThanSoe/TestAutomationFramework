import pytest
import logging
from datetime import datetime
from py.xml import html
from glob import glob
import re
import os

LOGGER = logging.getLogger(__name__)


def refactor(string: str) -> str:
    return string.replace("/", ".").replace("\\", ".").replace(".py", "")


pytest_plugins = [
    refactor(fixture) for fixture in glob("plugins/**/*.py", recursive=True) if "__" not in fixture
]


def pytest_configure(config):
    for path in config.getini("testpaths"):
        if not os.path.exists(path):
            os.makedirs(path)

    if config.option.showfixtures or config.option.collectonly:
        return
    timestamp = datetime.strftime(datetime.now(), '%Y-%m-%d_%H-%M-%S')
    if config.option.log_file is None:
        config.option.log_file = 'logs/' + timestamp + '.log'
    if config.option.htmlpath is None:
        config.option.htmlpath = 'logs/' + timestamp + '.html'
        config.option.self_contained_html = True
    if config.option.xmlpath is None:
        config.option.xmlpath = 'logs/' + timestamp + '.junit'


def pytest_html_report_title(report):
    report.title = "Test Report"

def pytest_html_results_summary(prefix, summary, postfix):
    prefix.extend([html.p("[VERSION]")])

def pytest_html_results_table_header(cells):
    cells.insert(2, html.th('Time', class_='sortable time', col='time'))
    cells.insert(2, html.th('Description'))


def pytest_html_results_table_row(report, cells):
    cells.insert(2, html.td(datetime.now(), class_='col-time'))
    if hasattr(report, "description"):
        cells.insert(2, html.td(report.description))
    else:
        cells.insert(2, html.td(""))


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    pytest_html = item.config.pluginmanager.getplugin('html')
    outcome = yield
    report = outcome.get_result()
    report.description = str(item.function.__doc__).strip()

    extra = getattr(report, 'extra', [])
    if report.when == 'call':
        # always add url to report
        test_id = str(item.parent.obj.__doc__).strip().partition('\n')[0]
        test_id_parts = re.match(r"^(\w*)-(\d*)$", test_id)
        if test_id_parts:
            extra.append(pytest_html.extras.url(f"https://tl-test.docker.ivu-ag.com/linkto.php?item=testcase&tprojectPrefix={test_id_parts[1]}&id={test_id_parts[0]}"))
        #xfail = hasattr(report, 'wasxfail')
        #if (report.skipped and xfail) or (report.failed and not xfail):
        #    # only add additional html on failure
        #    extra.append(pytest_html.extras.html('<div>Additional HTML</div>'))
        report.extra = extra
