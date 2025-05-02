"""Each module uses pytestmark to set the order for that module.
The tests inside each module will be executed in the same order as without ordering,
while the test modules will be ordered as defined in pytestmark, in this case in the order:
test_module3 -> test_module2 -> test_module1
"""
