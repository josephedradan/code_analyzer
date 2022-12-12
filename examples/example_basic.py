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
from code_analyzer import CodeAnalyzer

code_analyzer = CodeAnalyzer()  # Initialize analyzer
code_analyzer.start()

temp = 23123123131231

# Comment that will be displayed on the next line
code_analyzer.record_comment_for_interpretable_next("Class definition")


def fff():
    class X:

        def __init__(self):
            self.x = 2

        def __str__(self):
            return 'fdf'

    var_a = 2
    var_b = 3

    star = 123123123123

    def adder(temp_var):
        """
        From docstring
        :param temp_var:
        :return:
        """
        a = 424
        b = a + temp_var
        b = b + 5
        return b

    z = adder(100)
    final = z + var_a + var_b
    print(final)

    def out():
        f = 23
        q = 53

        def inner():
            z = f + 23 + q
            a = 23 + z
            return a

        return inner() + q

    var_c = out()
    print(var_c)


fff()

code_analyzer.stop()
code_analyzer.print()

# code_analyzer.get_code_analyzer_printer().print_debug()
code_analyzer.get_code_analyzer_printer().export_to_txt()

# code_analyzer.get_code_analyzer_printer().print_rich()  # export_rich_to_html prints to console by default
code_analyzer.get_code_analyzer_printer().export_rich_to_html()
