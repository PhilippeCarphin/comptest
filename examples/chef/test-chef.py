import comptest
import os
import argparse
p = argparse.ArgumentParser()
p.add_argument("--generated", action='store_true')
args = p.parse_args()

this_dir = os.path.dirname(__file__)

bash_comp = comptest.find_bash_completion()
init_file_basename = "_chef" if not args.generated else "_chef_generated"
c = comptest.CompletionRunner(
    init_files=[bash_comp, os.path.join(this_dir, init_file_basename)]
)

def test(cmd, expected, expect_failure=False):
    if isinstance(expected, str):
        result = c.get_comp(cmd)
    else:
        result = set(c.get_comp(cmd))
        expected = set(expected)
    global status

    if expect_failure:
        if result == expected:
            print(f"\033[31mFailure\033[0m: {cmd}: Expecting failure but result == expected")
            status = 1
        else:
            print(f"\033[32mSuccess\033[0m: {cmd}: Results diffrent from expected")
    else:
        if result != expected:
            print(f"\033[31mFailure\033[0m: {cmd}: expected {expected}, got {result}.")
            status = 1
        else:
            print(f"\033[32mSuccess\033[0m: {cmd}: got {result}")

test('chef ', ['cook', 'prep', '-h', '--help', '--debug', '-F'])
test('chef cook --vessel ', ['pan', 'pot'])
test('chef cook --temp ', ['high', 'medium', 'low'])
test('chef cook --bowl ', ['large', 'small'])
test('chef cook ', ['-h', '--help', '--vessel', '--temp', '--bowl'])
test('chef prep --bowl ', ['large', 'small'])
test('chef prep --vegetable ', ['onion', 'carrot', 'potato'])
test('chef prep ', ['-h', '--help', '--bowl', '--vegetable'])

