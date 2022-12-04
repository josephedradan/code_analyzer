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


@code_analyzer
def main():
    def add(x: int, y: int):
        code_analyzer.record_comment_for_interpretable_next({"Random ContainerComment": "Good code!"})
        result = x + y
        code_analyzer.record_comment_for_interpretable_previous({"result": result})

        for i in range(1):
            x = i

        return result

    add(1, 2)
    add(42, 8)
    add(5, 6)


if __name__ == '__main__':
    main()
    code_analyzer.print()
