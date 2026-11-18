
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

c.test('chef ', ['cook', 'prep', '-h', '--help', '--debug', '-d', '-F'])
c.test('chef cook ', ['-h', '--help', '--vessel', '-v', '--temp', '-t', '--bowl', '-b'])
c.test('chef cook --vessel ', ['pan', 'pot'])
c.test('chef cook -v ', ['pan', 'pot'])
c.test('chef cook --temp ', ['high', 'medium', 'low'])
c.test('chef cook -t ', ['high', 'medium', 'low'])
c.test('chef cook --bowl ', ['large', 'small'])
c.test('chef cook -b ', ['large', 'small'])
c.test('chef prep ', ['-h', '--help', '--bowl', '-b', '--vegetable', '-v'])
c.test('chef prep --bowl ', ['large', 'small'])
c.test('chef prep -b ', ['large', 'small'])
c.test('chef prep --vegetable ', ['onion', 'carrot', 'potato'])
c.test('chef prep -v ', ['onion', 'carrot', 'potato'])

sys.exit(1 if c.has_failed_tests else 0)
Namespace(debug=False, F=None)
