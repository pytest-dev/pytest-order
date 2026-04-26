# simple plugin that reverts the test order for testing indulgent ordering
def pytest_collection_modifyitems(config, items):
    items[:] = items[::-1]
