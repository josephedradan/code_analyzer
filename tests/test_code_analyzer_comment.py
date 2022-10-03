"""
Created by Joseph Edradan
Github: https://github.com/josephedradan

Date created: 9/12/2022

Purpose:

Details:

Description:

Notes:

IMPORTANT NOTES:

Explanation:

Tags:

Reference:

"""
# import pytest
from code_analyzer import CodeAnalyzer

# def _example_code_comments(code_analyzer: CodeAnalyzer):
#     def add(x, y):
#         code_analyzer.record_dict_for_line_next({"result comment 1": "Hello"})
#         code_analyzer.record_dict_for_line_next({"result comment 2": "Hello"})
#         result = x + y
#         code_analyzer.record_dict_for_line_previous({"result": result})
#
#         return x + y
#
#     result_0 = add(2, 4)
#
#     result_1 = add(1, result_0)
#
#
# @pytest.fixture(scope="module")  # scope="module" prevents setup on each test
# def fixture_callable_add() -> CodeAnalyzer:
#     code_analyzer = CodeAnalyzer()
#     code_analyzer.start()
#
#     _example_code_comments(code_analyzer)
#
#     code_analyzer.stop()
#     yield code_analyzer
#
#
# def _example_code_recursive(code_analyzer: CodeAnalyzer):
#     def recursive(depth):
#         if depth <= 0 or not isinstance(depth, int):
#             return depth
#
#         return recursive(depth - 1)
#
#     result = recursive(10)
#
#
# @pytest.fixture(scope="module")  # scope="module" prevents setup on each test
# def fixture_callable_recursive() -> CodeAnalyzer:
#     code_analyzer = CodeAnalyzer()
#     code_analyzer.start()
#
#     _example_code_comments(code_analyzer)
#
#     code_analyzer.stop()
#
#     yield code_analyzer
#
#
# # Will Break pytest
# @pytest.fixture(scope="module")  # scope="module" prevents setup on each test
# def fixture_code_analyzer() -> CodeAnalyzer:
#     code_analyzer = CodeAnalyzer()
#     code_analyzer.start()
#
#     yield code_analyzer
#
#     code_analyzer.stop()


def test_code_analyzer_comment_next_basic():
    """
    Test code_analyzer.record_dict_for_line_next()

    :return:
    """
    print()
    code_analyzer = CodeAnalyzer()
    code_analyzer.start()

    code_analyzer.record_dict_for_line_next({"Comment 1": "Hello", "Random Comment": "World"})
    x = 1

    code_analyzer.record_dict_for_line_next({"Comment 2": "Hello"})
    y = 2

    code_analyzer.record_dict_for_line_next({"Comment 3": "World"})
    z = x + y

    code_analyzer.stop()

    code_analyzer.print()

    for index, interpretable in enumerate(code_analyzer.get_list_interpretable()):
        dict_k_variable_v_value = interpretable.get_dict_k_variable_v_value()

        assert dict_k_variable_v_value.get(f"Comment {index + 1}") is not None


def test_code_analyzer_comment_next_multiple():
    """
    Test multiple code_analyzer.record_dict_for_line_next() calls for a single Interpretable

    :return:
    """
    print()
    code_analyzer = CodeAnalyzer()
    code_analyzer.start()

    code_analyzer.record_dict_for_line_next({"Comment 1": "Hello"})
    code_analyzer.record_dict_for_line_next({"Comment 2": "World"})
    x = 1

    code_analyzer.record_dict_for_line_next({"Comment 3": "Hello"})
    code_analyzer.record_dict_for_line_next({"Comment 4": "World"})
    y = 2

    code_analyzer.record_dict_for_line_next({"Comment 5": "Hello"})
    code_analyzer.record_dict_for_line_next({"Comment 6": "World"})
    z = x + y

    code_analyzer.stop()

    code_analyzer.print()

    for index, interpretable in enumerate(code_analyzer.get_list_interpretable()):
        dict_k_variable_v_value = interpretable.get_dict_k_variable_v_value()
        assert len(dict_k_variable_v_value) == 2


def test_code_analyzer_comment_previous_basic():
    """
    Test code_analyzer.record_dict_for_line_previous()

    :return:
    """
    print()
    code_analyzer = CodeAnalyzer()
    code_analyzer.start()

    x = 1
    code_analyzer.record_dict_for_line_previous({"x": x})

    y = 2
    code_analyzer.record_dict_for_line_previous({"y": y})

    z = x + y
    code_analyzer.record_dict_for_line_previous({"z": z})

    code_analyzer.stop()

    code_analyzer.print()

    assert code_analyzer.get_list_interpretable()[0].get_dict_k_variable_v_value().get("x") == 1
    assert code_analyzer.get_list_interpretable()[1].get_dict_k_variable_v_value().get("y") == 2
    assert code_analyzer.get_list_interpretable()[2].get_dict_k_variable_v_value().get("z") == 3


def test_code_analyzer_comment_overwrite():
    """
    Test multiple code_analyzer.record_dict_for_line_previous() and code_analyzer.record_dict_for_line_next() calls

    Notes:
        Some calls overwrite the previous values of the dict

    :return:
    """

    print()
    code_analyzer = CodeAnalyzer()
    code_analyzer.start()

    code_analyzer.record_dict_for_line_next({"Hello": "No"})
    code_analyzer.record_dict_for_line_next({"World": "More"})
    code_analyzer.record_dict_for_line_next({"Dude": "Memes"})
    x = 42
    code_analyzer.record_dict_for_line_previous({"Hello": "The"})
    code_analyzer.record_dict_for_line_previous({"World": "Flying"})
    code_analyzer.record_dict_for_line_previous({"Dude": "Cat"})

    code_analyzer.stop()

    code_analyzer.print()

    assert code_analyzer.get_list_interpretable()[0].get_dict_k_variable_v_value().get("Hello") == "The"
    assert code_analyzer.get_list_interpretable()[0].get_dict_k_variable_v_value().get("World") == "Flying"
    assert code_analyzer.get_list_interpretable()[0].get_dict_k_variable_v_value().get("Dude") == "Cat"


def test_code_analyzer_comment_function():
    """
    Test code_analyzer.record_dict_for_line_previous() and code_analyzer.record_dict_for_line_next() on a function

    :return:
    """
    print()
    code_analyzer = CodeAnalyzer()
    code_analyzer.start()

    code_analyzer.record_dict_for_line_next({"Comment on add function definition": "Hello"})

    def add(x: int, y: int):
        code_analyzer.record_dict_for_line_previous({"Comment on add function call": "World"})

        result = x + y
        code_analyzer.record_dict_for_line_previous({"result": result})

        return result

    code_analyzer.record_dict_for_line_next({"This should be on result_2 (1)": "Hello World"})
    result_2 = add(2, 3)
    code_analyzer.record_dict_for_line_previous({"This should be on result_2 (2)": result_2})

    code_analyzer.stop()

    code_analyzer.print()

    assert (code_analyzer
            .get_list_interpretable()[0]
            .get_dict_k_variable_v_value()
            .get("Comment on add function definition")) == "Hello"

    assert (code_analyzer
            .get_list_interpretable()[1]
            .get_dict_k_variable_v_value()
            .get("This should be on result_2 (1)")) == "Hello World"

    assert (code_analyzer
            .get_list_interpretable()[1]
            .get_dict_k_variable_v_value()
            .get("This should be on result_2 (2)")) == 5

    assert (code_analyzer
            .get_list_interpretable()[2]
            .get_dict_k_variable_v_value()
            .get("Comment on add function call")) == "World"

    assert (code_analyzer
            .get_list_interpretable()[3]
            .get_dict_k_variable_v_value()
            .get("result")) == 5
