"""
Created by Joseph Edradan
Github: https://github.com/josephedradan

Date created: 10/30/2022

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


def test_code_analyzer_scope_basic():
    """
    Testing if the scope depths are correct for a basic example

    :return:
    """

    code_analyzer = CodeAnalyzer()
    code_analyzer.start()

    def add(x: int, y: int) -> int:
        result = x + y

        code_analyzer.record_comment_for_interpretable_next({"result": result})

        return result

    result_final = add(add(add(add(1, 2), 3), 4), 5)

    code_analyzer.stop()
    code_analyzer.print()

    # *** THESE ARE THE CORRECT SCOPE DEPTHS FOR THE CODE ABOVE ***
    __SOLUTIONS = [0, 0, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1]

    _list_interpretable = code_analyzer.get_list_interpretable()

    for __SOLUTION, _interpretable in zip(__SOLUTIONS, _list_interpretable):
        assert _interpretable.get_scope_parent().get_indent_depth_scope() == __SOLUTION


def test_code_analyzer_scope_recursive():
    """
    Test if the scope depths are correct for a recursive example

    Notes:
        Just check the first and last Interpretables in this example because
        it's a simple recursive function

    :return:
    """

    code_analyzer = CodeAnalyzer()
    code_analyzer.start()

    def recursive(depth: int) -> int:
        if depth <= 0:
            code_analyzer.record_comment_for_interpretable_next({"depth": depth})

            return depth

        code_analyzer.record_comment_for_interpretable_next({"depth": depth - 1})
        return recursive(depth - 1)

    recursive(10)

    code_analyzer.stop()
    code_analyzer.print()

    _list_interpretable = code_analyzer.get_list_interpretable()

    assert _list_interpretable[0].get_scope_parent().get_indent_depth_scope() == 0
    assert _list_interpretable[0].get_scope_parent().get_indent_depth_corrected() == 0

    assert _list_interpretable[-1].get_scope_parent().get_indent_depth_scope() == 11
    assert _list_interpretable[-1].get_scope_parent().get_indent_depth_corrected() == 11


def test_code_analyzer_scope_complex():
    """
    Test the indent depth of
        get_indent_depth_scope()  # The actual scope depth
        get_indent_depth_corrected()  # The visual indent interpretation
    :return:
    """

    code_analyzer = CodeAnalyzer()
    code_analyzer.start()

    def add(x: int, y: int) -> int:
        result = x + y

        code_analyzer.record_comment_for_interpretable_next({"result": result})

        return result

    __CONDITION = True  # mimic conditions and scope depth

    if __CONDITION:
        if __CONDITION:
            if __CONDITION:
                if __CONDITION:
                    result_final = add(1, 2)

    code_analyzer.stop()
    code_analyzer.print()

    _list_interpretable = code_analyzer.get_list_interpretable()

    assert _list_interpretable[-1].get_scope_parent().get_indent_depth_scope() == 1
    assert _list_interpretable[-1].get_scope_parent().get_indent_depth_corrected() == 5


def test_code_analyzer_scope_recursive_complex():
    """
    Test if the scope depths and interpretable indents are correct for a recursive example with an indent offset
    caused by conditional statements

    :return:
    """

    code_analyzer = CodeAnalyzer()
    code_analyzer.start()

    __CONDITION = True  # mimic conditions and scope depth

    if __CONDITION:
        if __CONDITION:
            if __CONDITION:
                if __CONDITION:
                    def recursive(depth: int) -> int:
                        if depth <= 0:
                            code_analyzer.record_comment_for_interpretable_next({"depth": depth})

                            return depth

                        code_analyzer.record_comment_for_interpretable_next({"depth": depth - 1})
                        return recursive(depth - 1)

                    recursive(10)

    code_analyzer.stop()
    code_analyzer.print()

    _list_interpretable = code_analyzer.get_list_interpretable()

    assert _list_interpretable[0].get_scope_parent().get_indent_depth_scope() == 0
    assert _list_interpretable[0].get_scope_parent().get_indent_depth_corrected() == 0

    assert _list_interpretable[-1].get_scope_parent().get_indent_depth_scope() == 11
    assert _list_interpretable[-1].get_scope_parent().get_indent_depth_corrected() == 15

    assert _list_interpretable[0].get_trace_call_result_primary().get_indent_depth_corrected() == 0

    assert _list_interpretable[-1].get_trace_call_result_primary().get_indent_depth_corrected() == 16