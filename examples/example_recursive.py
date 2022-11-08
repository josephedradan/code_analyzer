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

code_analyzer = CodeAnalyzer()  # Initialize analyzer
code_analyzer.start()

# Comment that will be displayed on the next line
code_analyzer.record_dict_for_line_next({"Function definition here!": "Wow!"})


def recursive(depth: int) -> int:
    # Comment that will be displayed on the previous line
    code_analyzer.record_dict_for_line_previous({"depth": depth})
    if depth <= 0:
        code_analyzer.record_dict_for_line_next({"Final depth": depth})
        return depth

    return recursive(depth - 1)


code_analyzer.record_dict_for_line_next({"This is where the fun begins": "Oh no!"})
recursive(5)

code_analyzer.stop()
code_analyzer.print()
# code_analyzer.get_code_analyzer_printer().print_debug()