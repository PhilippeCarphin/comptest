
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

c.test('chef ', ['cook', 'prep', '-h', '--help', '--debug', '-d', '-F'])
c.test('chef cook ', ['-h', '--help', '--vessel', '-v', '--temp', '-t', '--bowl', '-b'])
c.test('chef cook --vessel ', ['pan', 'pot'])
c.test('chef cook --vessel _ ', ['pan', 'pot'], expect_failure=True)
c.test('chef cook -v ', ['pan', 'pot'])
c.test('chef cook -v _ ', ['pan', 'pot'], expect_failure=True)
c.test('chef cook --temp ', ['high', 'medium', 'low'])
c.test('chef cook --temp _ ', ['high', 'medium', 'low'], expect_failure=True)
c.test('chef cook -t ', ['high', 'medium', 'low'])
c.test('chef cook -t _ ', ['high', 'medium', 'low'], expect_failure=True)
c.test('chef cook --bowl ', ['large', 'small'])
c.test('chef cook --bowl _ ', ['large', 'small'], expect_failure=True)
c.test('chef cook -b ', ['large', 'small'])
c.test('chef cook -b _ ', ['large', 'small'], expect_failure=True)
c.test('chef prep ', ['-h', '--help', '--bowl', '-b', '--vegetable', '-v'])
c.test('chef prep --bowl ', ['large', 'small'])
c.test('chef prep --bowl _ ', ['large', 'small'])
c.test('chef prep --bowl _ _ ', ['large', 'small'])
c.test('chef prep --bowl _ _ _ -- ', ['large', 'small'], expect_failure=True)
c.test('chef prep -b ', ['large', 'small'])
c.test('chef prep -b _ ', ['large', 'small'])
c.test('chef prep -b _ _ ', ['large', 'small'])
c.test('chef prep -b _ _ _ -- ', ['large', 'small'], expect_failure=True)
c.test('chef prep --vegetable ', ['onion', 'carrot', 'potato'])
c.test('chef prep --vegetable _ ', ['onion', 'carrot', 'potato'], expect_failure=True)
c.test('chef prep -v ', ['onion', 'carrot', 'potato'])
c.test('chef prep -v _ ', ['onion', 'carrot', 'potato'], expect_failure=True)

sys.exit(1 if c.has_failed_tests else 0)
