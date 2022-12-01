"""
Created by Joseph Edradan
Github: https://github.com/josephedradan

Date created: 11/30/2022

Purpose:

Details:

Description:

Notes:

IMPORTANT NOTES:

Explanation:

Tags:

Reference:

"""

# IMPORTANT: THIS WILL PREVENT THE FUNCTION CALLS THAT THE TYPEUnion[None,int] WILL MAKE
from __future__ import annotations

from typing import Union

from code_analyzer import CodeAnalyzer

code_analyzer = CodeAnalyzer()  # Initialize analyzer
code_analyzer.start()


def fancy_recursive(current: int, current_next: Union[None, int] = None):
    code_analyzer.record_comment_for_interpretable_previous({"current": current, "current_next": current_next})

    code_analyzer.hide_interpretable_next()
    if current_next is None:
        code_analyzer.hide_interpretable_next()
        current_next = current - 1

    if current == 0:
        return current_next

    value = fancy_recursive(current - 1, current_next)

    if current - value == 1:
        fancy_recursive(value, value - 1)

    return value


fancy_recursive(10)

code_analyzer.stop()
code_analyzer.print()
code_analyzer.print_rich_and_export_rich()
