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

@code_analyzer
def main():
    def add(x: int, y: int):
        code_analyzer.record_dict_for_line_next({"Random Comment": "Good code!"})
        result = x + y
        code_analyzer.record_dict_for_line_previous({"result": result})

        return result

    add(1, 2)
    add(42, 8)
    add(5, 6)
    code_analyzer.record_dict_for_line_previous({"This is the last line of code": "But not the last interpretable"})


if __name__ == '__main__':
    main()
    code_analyzer.print()

