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

code_analyzer.record_comment_for_interpretable_next("Function Definition")


def recursive_complex(current: int, current_next: Union[None, int] = None):
    code_analyzer.record_comment_for_interpretable_previous({"current": current, "current_next": current_next})

    code_analyzer.hide_interpretable_next()
    if current_next is None:
        code_analyzer.hide_interpretable_next()
        current_next = current - 1

    if current == 0:
        code_analyzer.record_comment_for_interpretable_next(f"Returning value: {current_next}")
        return current_next

    value = recursive_complex(current - 1, current_next)

    if current - value == 1:  # Dank memes
        value = recursive_complex(value, value - 1)

    code_analyzer.record_comment_for_interpretable_next(value)
    return value


final_value = recursive_complex(10)
code_analyzer.record_comment_for_interpretable_next(final_value)
print(final_value)


code_analyzer.stop()
code_analyzer.print()
code_analyzer.print_rich_and_export_rich()
