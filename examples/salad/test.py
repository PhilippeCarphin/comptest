
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

c.test('salad ', ['-h', '--help', '--dressing', '-d', '--seasoning', '-s', '--vegetable', '-v', '--fruit', '-f'])
c.test('salad --dressing ', ['italian', 'ranch'])
c.test('salad -d ', ['italian', 'ranch'])
c.test('salad --seasoning ', ['salt', 'pepper'])
c.test('salad -s ', ['salt', 'pepper'])
c.test('salad --vegetable ', ['celery', 'carrot', 'broccoli', 'potato'])
c.test('salad -v ', ['celery', 'carrot', 'broccoli', 'potato'])
c.test('salad --fruit ', ['apple', 'apricot', 'banana', 'cherry'])
c.test('salad -f ', ['apple', 'apricot', 'banana', 'cherry'])

sys.exit(1 if c.has_failed_tests else 0)
