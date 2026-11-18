
import comptest
import os
import sys

bash_comp = comptest.find_bash_completion()
try:
    c = comptest.CompletionRunner(
        init_files=[bash_comp, sys.argv[1]],
    )
except RuntimeError as e:
    print(f"FAILURE: Init: {e}")
    raise SystemExit(1) from e

c.test('git ', ['push', 'remote', 'worktree', '-h', '--help', '--debug', '-d', '-F'])
c.test('git -F ', ['main-F', 'x'])
c.test('git push ', ['-h', '--help', '--color', '--all', '--random', 'upstream', 'origin'])
c.test('git push posart_0_value ', ['-h', '--help', '--color', '--all', '--random', 'main', 'dev'])
c.test('git push --color ', ['magenta', 'cyan', 'yellow'])
c.test('git remote ', ['add', 'remove', '-h', '--help'])
c.test('git remote add ', ['-h', '--help', '--name'])
c.test('git remote add --name ', ['remote-add--name', 'origin', 'upstream'])
c.test('git remote remove ', ['-h', '--help', '--name', '--force'])
c.test('git remote remove --name ', ['remote-remove--name', 'x'])
c.test('git remote remove --force ', ['remote-remove--force', 'x'])
c.test('git worktree ', ['add', 'delete', '-h', '--help'])
c.test('git worktree add ', ['-h', '--help', '--name'])
c.test('git worktree add --name ', ['worktree-add--name', 'x'])
c.test('git worktree delete ', ['-h', '--help', '--name'])
c.test('git worktree delete --name ', ['worktree-delete--name', 'x'])

sys.exit(1 if c.has_failed_tests else 0)
