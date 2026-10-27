
import comptest
bash_comp = comptest.find_bash_completion()
c = comptest.CompletionRunner(init_files=["examples/_salad", bash_comp])
status = 0
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

fruits = ['apple', 'apricot', 'banana', 'cherry']
veggies = ['celery', 'broccoli', 'carrot', 'potato']

test('salad --fruit ', fruits)
test('salad --fruit apple ', fruits)
test('salad --fruit apple banana ', fruits)
test('salad --fruit apple banana cherry ', fruits, expect_failure=True)
test('salad --fruit apple -- banana cherry ', fruits, expect_failure=True)

test('salad --vegetable ', veggies)
test('salad --vegetable potato carrot carrot potato carrot carrot carrot ', veggies)

test('salad --fruit a', ['apple', 'apricot'])
test('salad --fruit b', 'anana ')

