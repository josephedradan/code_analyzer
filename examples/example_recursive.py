"""
Created by Joseph Edradan
Github: https://github.com/josephedradan

Date created: 10/29/2022

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

code_analyzer = CodeAnalyzer()
code_analyzer.start()


def recursive(depth):
    code_analyzer.record_dict_for_line_previous({"Depth": depth})
    if depth <= 0:
        return depth

    return recursive(depth - 1)


if True:
    recursive(5)

code_analyzer.stop()
code_analyzer.print()
# code_analyzer.get_code_analyzer_printer().print_debug()
