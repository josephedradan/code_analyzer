"""
Created by Joseph Edradan
Github: https://github.com/josephedradan

Date created: 9/28/2022

Purpose:

Details:

Description:

Notes:

    Notes for code_analyzer.print():
        Exe Index Rel:  Execution Index Relative to the start()
        Line #:         Line Number in code
        Scope Depth:    Scope depth (How deep the scope is by index, it is based on a function's call)
        Indent lvl:     Indent Level (How deep the indent is)
        Exe Count:      Execution Count (Count of how many times a unique line has been executed)

IMPORTANT NOTES:

Explanation:

Tags:

Reference:

"""
from code_analyzer import CodeAnalyzer


def test_code_analyzer_if():
    """
    Test the last interpretable in a simple conditional
    :return:
    """

    code_analyzer = CodeAnalyzer()
    code_analyzer.start()

    x = 1

    if x:
        if x:
            if x:
                if x:
                    x = 2

    code_analyzer.stop()

    code_analyzer.print()

    _list_interpretable = code_analyzer.get_list_interpretable()

    assert _list_interpretable[-1].get_scope_parent().get_indent_depth_corrected() == 0
    assert _list_interpretable[-1].get_trace_call_result_primary().get_indent_level_corrected() == 4
    assert _list_interpretable[-1].get_execution_count() == 1


def test_code_analyzer_interpretable_recursive():
    """
    Test The second to last interpretable of a recursive function call

    :return:
    """
    code_analyzer = CodeAnalyzer()
    code_analyzer.start()

    def recursive(depth):
        code_analyzer.record_dict_for_line_previous({"Depth": depth})
        if depth <= 0:
            return depth

        return recursive(depth - 1)

    for i in range(5):
        recursive(5)

    code_analyzer.stop()

    code_analyzer.print()

    _list_interpretable = code_analyzer.get_list_interpretable()

    assert _list_interpretable[-2].get_scope_parent().get_indent_depth_corrected() == 6
    assert _list_interpretable[-2].get_trace_call_result_primary().get_indent_level_corrected() == 7
    assert _list_interpretable[-2].get_execution_count() == 30
