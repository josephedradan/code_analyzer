"""
Created by Joseph Edradan
Github: https://github.com/josephedradan

Date created: 9/28/2022

Purpose:
    Show how to use this analyzer

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


def add(x: int, y: int):
    result = x + y
    code_analyzer.record_dict_for_line_previous({"result": result})

    return result

add(1, 2)
add(42, 8)
add(5, 6)

code_analyzer.stop()
code_analyzer.print()
