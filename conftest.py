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
    refactor(fixture) for fixture in glob("precon/**/*.py", recursive=True) if "__" not in fixture
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
