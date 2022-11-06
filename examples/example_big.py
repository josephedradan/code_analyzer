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
from code_analyzer import CodeAnalyzer


# @code_analyzer.decorator_ignore_callable
def add(x, y):
    result = x + y
    return result


def recursive_call(value: int):
    if isinstance(value, int):
        if value > 0:
            return recursive_call(value - 1)
        return value
    return 0


def function():
    i = 12312

    print("Hi")  # Random print

    x = 20

    class Annie():
        pass

    class Outer:
        class Josh:

            def get_nothing(self) -> str:
                return "You Just go None"

            def __str__(self):
                return "Josh's Name"

            def __init__(self):
                x = "Hi from init"
                pass

            pass  # This is the return

    Josh = Outer.Josh

    josh = Josh()

    josh.get_nothing()

    code_analyzer.record_dict_for_line_next({"x VALUE 1 ON for": x})
    code_analyzer.record_dict_for_line_next({"x VALUE 2 ON for": x})

    code_analyzer.record_dict_for_line_previous({"FFFF 1 ON x": i})
    code_analyzer.record_dict_for_line_previous({"FFFF 2 ON x": i})

    # The belwo does not include the additional lines that complete the statement
    testing = (
        2, 4, "dsfsd"
    )

    for i in range(4):
        print(i)
        code_analyzer.record_dict_for_line_next({"TESTING ON x += 1": "uhhh..."})

        code_analyzer.record_dict_for_line_previous({"i VALUE 1 ON for": i})
        code_analyzer.record_dict_for_line_previous({"i VALUE 2 ON for": i})

        x += 1

        x
        print()

        code_analyzer.record_dict_for_line_next({"IM ON TOP": "YO"})
        z = add(i, x)

        code_analyzer.record_dict_for_line_previous({"z VALUE": z})

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
    code_analyzer.record_dict_for_line_next({"1 SHOULD BE ON bob = Bob()": "TEST 1"})

    bob = Bob()
    code_analyzer.record_dict_for_line_previous({"2 SHOULD BE ON bob = Bob()": "TEST 2"})
    code_analyzer.record_dict_for_line_previous({"3 SHOULD BE ON bob = Bob()": "TEST 3"})

    last_line = 2323

    def ret():

        _inner = "_inner"

        def ret_inner():
            _inner_2 = "_inner_2"

            return _inner_2

        return ret_inner()

    ret()
    code_analyzer.record_dict_for_line_previous({"SHOULD BE ON ret()": "HELLO"})
    code_analyzer.record_dict_for_line_next({"SHOULD BE ON print": "HELLO"})

    print("RECURSIVE CALL TESTING")

    recursive_call(4)

    def idk():
        code_analyzer.record_dict_for_line_previous({"SHOULD BE ON CALLABLE'S HEAD": "JOSEPH"})

        def yo():
            _x = 24
            return 2

        print("WHEN AM I CALLED?")

        code_analyzer.record_dict_for_line_next({"ON RETURN I THINK": "JOSEPH"})

        return yo()

    idk()
    code_analyzer.record_dict_for_line_previous({"ON idk()": "JOSEPH"})

    def empty():
        x = 2
        z = x + 2

        print("YO")
        # code_analyzer.record_dict_for_line_previous({"ON x = 2": "JOSEPH"})
        code_analyzer.record_dict_for_line_next({"ON return?": "JOSEPH"})
        # pass

    empty()

    def yee():
        x = 2
        code_analyzer.record_dict_for_line_next({"ON x = 2 (1))": "JOSEPH"})
        code_analyzer.record_dict_for_line_previous({"ON x = 2 (2)": "JOSEPH"})
        code_analyzer.record_dict_for_line_next({"ON x = 2 (3)": "JOSEPH"})

    yee()

    def yee2():
        # x = 2
        code_analyzer.record_dict_for_line_next({"Testing next 1": "JOSEPH"})
        code_analyzer.record_dict_for_line_next({"Testing next 2": "JOSEPH"})
        # code_analyzer.record_dict_for_line_previous({"ON yee2() 2123123 2": "JOSEPH"})

    yee2()

    print("BEFORE THE ENDING")
    print("ENDING")


if __name__ == '__main__':
    code_analyzer = CodeAnalyzer()
    code_analyzer.start()
    function()
    code_analyzer.stop()
    code_analyzer.print()
