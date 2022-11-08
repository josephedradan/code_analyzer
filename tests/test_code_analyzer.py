"""
Created by Joseph Edradan
Github: https://github.com/josephedradan

Date created: 9/27/2022

Purpose:

Details:

Description:

Notes:

IMPORTANT NOTES:

    USING print() when using the code analyzer in pytest will print some strange stuff...

Explanation:

Tags:

Reference:

"""
from typing import Union

import pytest
from code_analyzer import CodeAnalyzer
from code_analyzer.code_analyzer import NoScopeAvailable

def test_code_analyzer_no_code():
    """
    Test the analyzer when there is no code to analyze

    Notes:
        Basically, the code should not crash

    :return:
    """

    code_analyzer = CodeAnalyzer()
    code_analyzer.start()
    code_analyzer.stop()
    code_analyzer.print()

    assert len(code_analyzer.list_interpretable) == 0
    assert len(code_analyzer.get_list_interpretable()) == 0


def test_code_analyzer_basic():
    """
    Test if the code_analyzer.start() and code_analyzer.stop() work as intended.

    Notes:
        In the example below, there should be 8 interpretables in total

        Exe Index Rel     Code + {Variable: Value}
            0                        x = 1
            1                        y = 2
            2                        def add(x: int, y: int):
            3                        result = add(x, y)
            4                        def add(x: int, y: int):
            5                            _result = x + y
            6                            return _result
            7                        result = result + 1

    :return:
    """

    print()

    code_analyzer = CodeAnalyzer()
    code_analyzer.start()

    x = 1
    y = 2

    def add(x: int, y: int):
        _result = x + y

        return _result

    result = add(x, y)

    result = result + 1

    code_analyzer.stop()
    code_analyzer.print()

    assert len(code_analyzer.list_interpretable) == 8


def test_code_analyzer_on_a_class():
    """
    Test if the analyzer can correctly identify and handle a class definition

    :return:
    """

    code_analyzer = CodeAnalyzer()
    code_analyzer.start()

    class Person:
        def __init__(self, name: str):
            self.name = name
            pass

        def function(self, x: int) -> int:
            x += 1
            y = "This should be an interpretable unless this method is called"
            return x

    code_analyzer.stop()
    code_analyzer.print()

    assert len(code_analyzer.list_interpretable) == 3


def test_code_analyzer_stop_inner():
    """
    Test if the code_analyzer.start() and code_analyzer.stop() work as intended.
    code_analyzer.stop() is located inside the code being testing

    Notes:
        In the example below, there should be 6 interpretables in total

        Exe Index Rel     Code + {Variable: Value}
            0                        x = 1
            1                        y = 2
            2                        def add(x: int, y: int):
            3                        result = add(x, y)
            4                        def add(x: int, y: int):
            5                            _result = x + y

    :return:
    """

    print()

    code_analyzer = CodeAnalyzer()
    code_analyzer.start()

    x = 1
    y = 2

    def add(x: int, y: int):
        _result = x + y

        code_analyzer.stop()

        return _result

    result = add(x, y)

    result = result + 1

    code_analyzer.print()

    assert len(code_analyzer.list_interpretable) == 6


def test_code_analyzer_deep():
    """
    Test if the code_analyzer.start() and code_analyzer.stop() work as intended.
    Both methods are deep in a function.

    Notes:
        In the example below, there should be 8 interpretables in total

        Exe Index Rel     Code + {Variable: Value}
            0                        x = 1
            1                        y = 2
            2                        def add(x: int, y: int):
            3                        result = add(x, y)
            4                        def add(x: int, y: int):
            5                            _result = x + y
            6                            return _result
            7                        result = result + 1

    :return:
    """

    print()

    code_analyzer: Union[CodeAnalyzer, None] = None

    def inner_0():
        def inner_1():
            def inner_2():
                nonlocal code_analyzer

                code_analyzer = CodeAnalyzer()
                code_analyzer.start()

                x = 1
                y = 2

                def add(x: int, y: int):
                    _result = x + y

                    return _result

                result = add(x, y)

                result = result + 1

                code_analyzer.stop()

            inner_2()

        inner_1()

    inner_0()

    code_analyzer.print()

    assert len(code_analyzer.list_interpretable) == 8


def test_code_analyzer_deep_exception_no_scope_available():
    """
    Test if the code_analyzer.start() and code_analyzer.stop() work as intended.
    code_analyzer.stop() is on a higher scope which should raise an exception.

    :return:
    """

    print()

    with pytest.raises(NoScopeAvailable):
        code_analyzer: Union[CodeAnalyzer, None] = None

        def inner_0():
            def inner_1():
                def inner_2():
                    nonlocal code_analyzer

                    code_analyzer = CodeAnalyzer()
                    code_analyzer.start()

                    x = 1
                    y = 2

                inner_2()

            inner_1()
            code_analyzer.stop()

        inner_0()

        code_analyzer.print()


def test_code_analyzer_with():
    """
    Test using the "with" keyword instead of the start() and stop() methods (Note that both of these methods
    are called inside the "with" scope)

    Notes:
        In the example below, there should be 8 interpretables in total

        Exe Index Rel     Code + {Variable: Value}
            0                        x = 1
            1                        y = 2
            2                        def add(x: int, y: int):
            3                        result = add(x, y)
            4                        def add(x: int, y: int):
            5                            _result = x + y
            6                            return _result
            7                        result = result + 1

    :return:
    """
    print()
    code_analyzer = CodeAnalyzer()

    with code_analyzer as ca:
        x = 1
        y = 2

        def add(x: int, y: int):
            _result = x + y

            return _result

        result = add(x, y)

        result = result + 1

    ca.print()

    assert len(code_analyzer.list_interpretable) == 8


def test_code_analyzer_with_stop_inner():
    """
    Test using the "with" keyword instead of the start() and stop() methods (Note that both of these methods
    are called inside the "with" scope)

    Notes:
        In the example below, there should be 8 interpretables in total

        Exe Index Rel     Code + {Variable: Value}
            0                        x = 1
            1                        y = 2
            2                        def add(x: int, y: int):
            3                        result = add(x, y)
            4                        def add(x: int, y: int):
            5                            _result = x + y

    :return:
    """
    print()
    code_analyzer = CodeAnalyzer()

    with code_analyzer as ca:
        x = 1
        y = 2

        def add(x: int, y: int):
            _result = x + y

            code_analyzer.stop()

            return _result

        result = add(x, y)

        result = result + 1

    ca.print()

    assert len(code_analyzer.list_interpretable) == 6


def test_code_analyzer_with_deep():
    """
    Test using the "with" keyword instead of the start() and stop() methods (Note that both of these methods
    are called inside the "with" scope)

    Notes:
        In the example below, there should be 8 interpretables in total

        Exe Index Rel     Code + {Variable: Value}
            0                        x = 1
            1                        y = 2
            2                        def add(x: int, y: int):
            3                        result = add(x, y)
            4                        def add(x: int, y: int):
            5                            _result = x + y
            6                            return _result
            7                        result = result + 1

    :return:
    """
    print()
    code_analyzer = CodeAnalyzer()

    def inner_0():
        def inner_1():
            def inner_2():
                nonlocal code_analyzer

                with code_analyzer:
                    x = 1
                    y = 2

                    def add(x: int, y: int):
                        _result = x + y

                        return _result

                    result = add(x, y)

                    result = result + 1

            inner_2()

        inner_1()

    inner_0()

    code_analyzer.print()

    assert len(code_analyzer.list_interpretable) == 8


def test_code_analyzer_decorator():
    """
    Test using the CodeAnalyser object as a decorator

    Notes:
        In the example below, there should be 8 interpretables in total

        Exe Index Rel     Code + {Variable: Value}
            0                        x = 1
            1                        y = 2
            2                        def add(x: int, y: int):
            3                        result = add(x, y)
            4                        def add(x: int, y: int):
            5                            _result = x + y
            6                            return _result
            7                        result = result + 1

    :return:
    """
    print()
    code_analyzer = CodeAnalyzer()

    @code_analyzer
    def main():
        x = 1
        y = 2

        def add(x: int, y: int):
            _result = x + y

            return _result

        result = add(x, y)

        result = result + 1

    main()

    code_analyzer.print()

    assert len(code_analyzer.list_interpretable) == 8