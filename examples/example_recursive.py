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

# ContainerComment that will be displayed on the next line
code_analyzer.record_comment_for_interpretable_next({"Function definition here!": "Wow!"})


def recursive(depth: int) -> int:
    # ContainerComment that will be displayed on the previous line
    code_analyzer.record_comment_for_interpretable_previous({"__depth": depth})
    if depth <= 0:
        code_analyzer.record_comment_for_interpretable_next({"Final depth": depth})
        return depth

    return recursive(depth - 1)


code_analyzer.record_comment_for_interpretable_next({"This is where the fun begins": "Oh no!"})
recursive(5)

code_analyzer.stop()
code_analyzer.print()

# code_analyzer.get_code_analyzer_printer().print_debug()
code_analyzer.get_code_analyzer_printer().export_to_txt()

# code_analyzer.get_code_analyzer_printer().print_rich()  # export_rich_to_html prints to console by default
code_analyzer.get_code_analyzer_printer().export_rich_to_html()