"""
Created by Joseph Edradan
Github: https://github.com/josephedradan

Date created: 9/28/2022

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

with code_analyzer as ca:
    def add(x: int, y: int):

        code_analyzer.record_dict_for_line_next({"Random Comment": "Good code!"})
        result = x + y
        ca.record_dict_for_line_previous({"result": result})

        return result

    add(1, 2)
    add(42, 8)
    add(5, 6)

code_analyzer.print()