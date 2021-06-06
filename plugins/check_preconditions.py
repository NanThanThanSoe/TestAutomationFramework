import logging

from plugins.func_preconditions import capabilitiy_lists, filter_unexecutable_items, filter_empty_lists

LOGGER = logging.getLogger(__name__)


def pytest_collection_modifyitems(session, config, items):

    fixtures = list(set([fixture for item in items for fixture in item.fixturenames]))
    scope, _ = capabilitiy_lists(fixtures)
    deselected_items = []
    for item in items:
        fixtures_require_preconditions = [operation for operation in item.fixturenames if operation in scope]
        deselect_items = filter_unexecutable_items(fixtures_require_preconditions, item)
        deselected_items.append(deselect_items)
        if 'scp_put_tmp' in item.fixturenames:
            item.fixturenames.append("check_scp_put_tmp_after_setup")

    deselected_lst = filter_empty_lists(deselected_items)
    LOGGER.info(f'Deselected items {deselected_lst}')
    #config.hook.pytest_deselected(items=deselected_lst)   
