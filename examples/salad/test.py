
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

c.test('salad ', ['-h', '--help', '--dressing', '-d', '--seasoning', '-s', '--vegetable', '-v', '--fruit', '-f'])
c.test('salad --dressing ', ['italian', 'ranch'])
c.test('salad --dressing _ ', ['italian', 'ranch'], expect_failure=True)
c.test('salad -d ', ['italian', 'ranch'])
c.test('salad -d _ ', ['italian', 'ranch'], expect_failure=True)
c.test('salad --seasoning ', ['salt', 'pepper'])
c.test('salad --seasoning _ ', ['salt', 'pepper'])
c.test('salad --seasoning _ _ ', ['salt', 'pepper'])
c.test('salad --seasoning _ _ _ -- ', ['salt', 'pepper'], expect_failure=True)
c.test('salad -s ', ['salt', 'pepper'])
c.test('salad -s _ ', ['salt', 'pepper'])
c.test('salad -s _ _ ', ['salt', 'pepper'])
c.test('salad -s _ _ _ -- ', ['salt', 'pepper'], expect_failure=True)
c.test('salad --vegetable ', ['celery', 'carrot', 'broccoli', 'potato'])
c.test('salad --vegetable _ ', ['celery', 'carrot', 'broccoli', 'potato'])
c.test('salad --vegetable _ _ ', ['celery', 'carrot', 'broccoli', 'potato'])
c.test('salad --vegetable _ _ _ -- ', ['celery', 'carrot', 'broccoli', 'potato'], expect_failure=True)
c.test('salad -v ', ['celery', 'carrot', 'broccoli', 'potato'])
c.test('salad -v _ ', ['celery', 'carrot', 'broccoli', 'potato'])
c.test('salad -v _ _ ', ['celery', 'carrot', 'broccoli', 'potato'])
c.test('salad -v _ _ _ -- ', ['celery', 'carrot', 'broccoli', 'potato'], expect_failure=True)
c.test('salad --fruit ', ['apple', 'apricot', 'banana', 'cherry'])
c.test('salad --fruit _ ', ['apple', 'apricot', 'banana', 'cherry'])
c.test('salad --fruit _ _ ', ['apple', 'apricot', 'banana', 'cherry'])
c.test('salad --fruit _ _ _ ', ['apple', 'apricot', 'banana', 'cherry'], expect_failure=True)
c.test('salad -f ', ['apple', 'apricot', 'banana', 'cherry'])
c.test('salad -f _ ', ['apple', 'apricot', 'banana', 'cherry'])
c.test('salad -f _ _ ', ['apple', 'apricot', 'banana', 'cherry'])
c.test('salad -f _ _ _ ', ['apple', 'apricot', 'banana', 'cherry'], expect_failure=True)

sys.exit(1 if c.has_failed_tests else 0)
