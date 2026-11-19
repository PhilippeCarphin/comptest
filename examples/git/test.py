
import comptest
import sys

bash_comp = comptest.find_bash_completion()
try:
    c = comptest.CompletionRunner(
        init_files=[bash_comp, sys.argv[1]],
        PS4='+ \033[35m${BASH_SOURCE[0]##*/}\033[36m:\033[1;37m${FUNCNAME:-}\033[22;36m:\033[32m${LINENO:-x}\033[36m:\033[0m ',
        xtrace_log="xtrace.log",
        logfile="pty.log"
    )
except RuntimeError as e:
    print(f"FAILURE: Init: '{e}'")
    raise SystemExit(1) from e

c.test('git ', ['push', 'remote', 'worktree', '-h', '--help', '--debug', '-d', '-F'])
c.test('git -F ', ['main-F', 'x'])
c.test('git -F _ ', ['main-F', 'x'], expect_failure=True)
c.test('git push ', ['-h', '--help', '--color', '--all', '--random', 'upstream', 'origin'])
c.test('git push posart_0_value ', ['-h', '--help', '--color', '--all', '--random', 'main', 'dev'])
c.test('git push --color ', ['magenta', 'cyan', 'yellow'])
c.test('git push --color _ ', ['magenta', 'cyan', 'yellow'])
c.test('git push --color _ _ ', ['magenta', 'cyan', 'yellow'], expect_failure=True)
c.test('git remote ', ['add', 'remove', '-h', '--help'])
c.test('git remote add ', ['-h', '--help', '--name'])
c.test('git remote add --name ', ['remote-add--name', 'origin', 'upstream'])
c.test('git remote add --name _ ', ['remote-add--name', 'origin', 'upstream'], expect_failure=True)
c.test('git remote remove ', ['-h', '--help', '--name', '--force'])
c.test('git remote remove --name ', ['remote-remove--name', 'x'])
c.test('git remote remove --name _ ', ['remote-remove--name', 'x'])
c.test('git remote remove --name _ _ ', ['remote-remove--name', 'x'])
c.test('git remote remove --name _ _ _ ', ['remote-remove--name', 'x'], expect_failure=True)
c.test('git remote remove --force ', ['remote-remove--force', 'x'])
c.test('git remote remove --force _ ', ['remote-remove--force', 'x'], expect_failure=True)
c.test('git worktree ', ['add', 'delete', '-h', '--help'])
c.test('git worktree add ', ['-h', '--help', '--name'])
c.test('git worktree add --name ', ['worktree-add--name', 'x'])
c.test('git worktree add --name _ ', ['worktree-add--name', 'x'], expect_failure=True)
c.test('git worktree delete ', ['-h', '--help', '--name'])
c.test('git worktree delete --name ', ['worktree-delete--name', 'x'])
c.test('git worktree delete --name _ ', ['worktree-delete--name', 'x'], expect_failure=True)

sys.exit(1 if c.has_failed_tests else 0)
