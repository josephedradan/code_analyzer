"""
Created by Joseph Edradan
Github: https://github.com/josephedradan

Date created: 5/21/2022

Purpose:

Details:

Description:

Notes:

IMPORTANT NOTES:

Explanation:

Tags:

Reference:

"""
from code_analyzer import PythonCodeAnalyzer

python_code_analyzer = PythonCodeAnalyzer()
python_code_analyzer.start()


# @python_code_analyzer.decorator_ignore_callable
def add(x, y):
    return x + y


def recursive_call(value: int):
    if isinstance(value, int):
        if value > 0:
            return recursive_call(value - 1)
        return value
    return 0


def function():
    i = 12312

    print("Fuck")  # Random Comment

    x = 20

    class Annie():
        pass

    class Outer:
        class Josh:

            def get_nothing(self) -> str:
                return "YOu Just go None"

            def __str__(self):
                return "Josh's Name"

            def __init__(self):
                x = "Hi from init"
                pass

            pass  # This is the return

    Josh = Outer.Josh

    josh = Josh()

    josh.get_nothing()

    python_code_analyzer.record_dict_for_line_next({"x VALUE 1 ON for": x})
    python_code_analyzer.record_dict_for_line_next({"x VALUE 2 ON for": x})

    python_code_analyzer.record_dict_for_line_previous({"FFFF 1 ON x": i})
    python_code_analyzer.record_dict_for_line_previous({"FFFF 2 ON x": i})

    # The belwo does not include the additional lines that complete the statement
    testing = (
        2, 4, "dsfsd"
    )

    for i in range(4):
        print(i)
        python_code_analyzer.record_dict_for_line_next({"TESTING ON x += 1": "uhhh..."})

        python_code_analyzer.record_dict_for_line_previous({"i VALUE 1 ON for": i})
        python_code_analyzer.record_dict_for_line_previous({"i VALUE 2 ON for": i})

        x += 1

        x
        print()

        python_code_analyzer.record_dict_for_line_next({"IM ON TOP": "YO"})
        z = add(i, x)

        python_code_analyzer.record_dict_for_line_previous({"z VALUE": z})

        print(z)

    b1 = "Something 1"

    f1 = 0

    while f1 < 3:
        f1 += 1

    b2 = "Something 2"

    f2 = 0

    while True:  # "while True and x > 0" Does get caught by the trace callback function but "while True" does not
        if f2 > 3:
            break
        f2 += 1

    for i in range(10):

        if i == 2:
            break

    print()

    class Bob():

        def __init__(self):
            self.x = 23

    dude = 233333
    python_code_analyzer.record_dict_for_line_next({"1 SHOULD BE ON bob = Bob()": "TEST 1"})

    bob = Bob()
    python_code_analyzer.record_dict_for_line_previous({"2 SHOULD BE ON bob = Bob()": "TEST 2"})
    python_code_analyzer.record_dict_for_line_previous({"3 SHOULD BE ON bob = Bob()": "TEST 3"})

    last_line = 2323

    def ret():

        _inner = "_inner"

        def ret_inner():
            _inner_2 = "_inner_2"

            return _inner_2

        return ret_inner()

    ret()
    python_code_analyzer.record_dict_for_line_previous({"SHOULD BE ON ret()": "HELLO"})
    python_code_analyzer.record_dict_for_line_next({"SHOULD BE ON print": "HELLO"})

    print("RECURSIVE CALL TESTING")

    recursive_call(4)

    def idk():
        python_code_analyzer.record_dict_for_line_previous({"SHOULD BE ON CALLABLE'S HEAD": "JOSEPH"})
        def yo():
            _x = 24
            return 2

        print("WHEN AM I CALLED?")

        python_code_analyzer.record_dict_for_line_next({"ON RETURN I THINK": "JOSEPH"})

        return yo()

    idk()
    python_code_analyzer.record_dict_for_line_previous({"ON idk()": "JOSEPH"})

    def empty():
        x = 2
        z = x + 2

        print("YO")
        # python_code_analyzer.record_dict_for_line_previous({"ON x = 2": "JOSEPH"})
        python_code_analyzer.record_dict_for_line_next({"ON return?": "JOSEPH"})
        # pass
    empty()

    def yee():
        x = 2
        python_code_analyzer.record_dict_for_line_previous({"ON return? 2": "JOSEPH"})
    yee()

    def yee2():
        # x = 2
        python_code_analyzer.record_dict_for_line_next({"Testing next 1": "JOSEPH"})
        python_code_analyzer.record_dict_for_line_next({"Testing next 2": "JOSEPH"})
        # python_code_analyzer.record_dict_for_line_previous({"ON yee2() 2123123 2": "JOSEPH"})
    yee2()

    print("BEFORE THE ENDING")
    print("ENDING")


if __name__ == '__main__':
    a = "This is now shown, which is technically wrong"
    function()

    python_code_analyzer.stop()

    print("THIS TraceCallResult AND THEREFORE Interpretable SHOULD NOT EXIST")

    python_code_analyzer.print()
