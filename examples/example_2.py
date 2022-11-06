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
    code_analyzer.record_dict_for_line_previous({'This should be on "def add(x: int, y: int)" (1)': "Good code!"})
    code_analyzer.record_dict_for_line_next({'This should be on "def add(x: int, y: int)" (2)': "Good code!"})


    def add(x: int, y: int):
        code_analyzer.record_dict_for_line_next({"Random Comment": "Good code!"})
        result = x + y
        ca.record_dict_for_line_previous({"result": result})

        for i in range(1):
            x = i

        return result


    add(1, 2)
    add(42, 8)
    add(5, 6)

code_analyzer.print()
