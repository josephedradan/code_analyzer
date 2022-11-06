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

code_analyzer = CodeAnalyzer()
code_analyzer.start()


def recursive(depth):
    # code_analyzer.record_dict_for_line_previous({"Depth": depth})
    if depth <= 0:
        return depth

    return recursive(depth - 1)


if True:
    recursive(5)

code_analyzer.stop()
code_analyzer.print()
#
# def main():
#     code_analyzer = CodeAnalyzer()
#     code_analyzer.start()
#
#
#
#     def recursive(x):
#         if x <= 0:
#             return x
#
#         return recursive(x -1)
#
#     recursive(10)
#
#     code_analyzer.stop()
#     code_analyzer.print()
#
# if __name__ == '__main__':
#     main()