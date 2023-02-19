"""
Date created: 9/28/2022

Purpose:
    Show how to use this analyzer

Details:

Description:

Notes:

IMPORTANT NOTES:

Explanation:

Tags:

Contributors:
    https://github.com/josephedradan

Reference:

"""

from code_analyzer import CodeAnalyzer

code_analyzer = CodeAnalyzer()


@code_analyzer
def main():
    code_analyzer.record_comment_for_interpretable_next("Function defined")

    def add(x: int, y: int):
        result = x + y
        code_analyzer.record_comment_for_interpretable_previous({"result": result})
        code_analyzer.record_comment_for_interpretable_previous(f"Result {result}")

        for i in range(1):
            x = i

        return result

    add(1, 2)
    add(42, 8)
    add(5, 6)


if __name__ == '__main__':
    main()
    code_analyzer.print()
