import comptest
import os

this_dir=os.path.dirname(__file__)
bash_comp = comptest.find_bash_completion()

try:
    c = comptest.CompletionRunner(
        init_files=[bash_comp, os.path.join(this_dir, "generated_comp.bash")]
    )
except RuntimeError as e:
    print(f"FAILURE: Init: {e}")
    raise SystemExit(1) from e

def compare_sets(a,b):
    a = set(a)
    b = set(b)

    common = a.intersection(b)
    just_a = a - b
    just_b = b - a
    print(f"\033[1;37mEXPECTED\033[0m {{\033[32m{','.join(common)},\033[31m{','.join(just_a)}\033[0m}} \033[1;37mGOT: \033[0m {{\033[32m{','.join(common)}, \033[31m{','.join(just_b)}\033[0m}}")
def test(cmd, expected, expect_failure=False):
    if isinstance(expected, str):
        result = c.get_comp(cmd)
    else:
        result = c.get_comp(cmd, cut_descriptions=True)
        if isinstance(result, str) or result is None:
            print(f"Expected {expected}, got {result!r}")
        else:
            compare_sets(expected, result)
    global status

test('git ', ['remote', 'worktree', '-h', '--help', '--debug', '-d', '-F'])
test('git -F ', ['main-F', 'x'])
test('git remote ', ['add', 'remove', '-h', '--help'])
test('git remote add ', ['-h', '--help', '--name'])
test('git remote add --name ', ['remote-add--name', 'origin', 'upstream'])
test('git remote remove ', ['-h', '--help', '--name', '--force'])
test('git remote remove --name ', ['remote-remove--name', 'x'])
test('git remote remove --force ', ['remote-remove--force', 'x'])
test('git worktree ', ['add', 'delete', '-h', '--help'])
test('git worktree add ', ['-h', '--help', '--name'])
test('git worktree add --name ', ['worktree-add--name', 'x'])
test('git worktree delete ', ['-h', '--help', '--name'])
test('git worktree delete --name ', ['worktree-delete--name', 'x'])
