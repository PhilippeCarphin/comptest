#!/usr/bin/env python3

import sys
import os
import logging

this_dir=os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.normpath(os.path.join(this_dir, '..', 'src', 'python')))

import comptest
# logging.basicConfig(
#     format="[{levelname} - {funcName}] {message}",
#     style='{',
#     level=logging.DEBUG
# )

bash_comp = comptest.find_bash_completion()
os.environ['XDG_DATA_DIRS'] = os.path.join(this_dir, 'share')
print(f"XDG_DATA_DIRS: {os.environ['XDG_DATA_DIRS']}")

c = comptest.CompletionRunner(
        init_files=[bash_comp],
        xtrace=True, logfile="termoutput")
results=[]
def test(cmd, expected, timeout=None):
    comp = c.get_comp_magic(cmd, timeout=timeout)
    if isinstance(comp, list):
        passed = set(expected) == set(comp)
    elif isinstance(comp, str):
        passed = comp == expected
    elif comp is None:
        passed = expected is None

    if not passed:
        print(f"Completion for '{cmd}' failed: expected '{expected}', got '{comp}'")

test('salad ', ['-fruit', '-vegetable'])
test('salad -fruit ', ['apple', 'apricot', 'banana', 'cherry'])
test('salad -vegetable ', ['carrot', 'celery', 'onion', 'potato'])
test('salad -fruit ban', 'ana ')
test('salad -vegetable o', 'nion ', timeout=1)
