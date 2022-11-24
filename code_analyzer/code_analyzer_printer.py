"""
Created by Joseph Edradan
Github: https://github.com/josephedradan

Date created: 11/6/2022

Purpose:

Details:

Description:

Notes:


IMPORTANT NOTES:

Explanation:

Tags:

Reference:

"""

from __future__ import annotations

import os
import sys
from enum import Enum
from typing import List, Union, Callable, Literal, Tuple, Generator

import code_analyzer as _code_analyzer
import colorama
import pandas as pd
from code_analyzer import constants
from code_analyzer.interpretable import Interpretable
from code_analyzer.trace_call_result import TraceCallResult
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

colorama.init()

PRINT_FORMAT_STR_EXECUTION_ANALYSIS = "{:<16}{:<10}{:<14}{:<14}{:<18}{} {}"

BORDER_SPACE_PRIMARY_KEY = "#"
BORDER_SPACE_SECONDARY_KEY = "-"

BORDER_SPACE_PRIMARY_AMOUNT = 100
BORDER_SPACE_SECONDARY_AMOUNT = 50

BORDER_SPACE_PRIMARY = BORDER_SPACE_PRIMARY_KEY * BORDER_SPACE_PRIMARY_AMOUNT
BORDER_SPACE_SECONDARY = BORDER_SPACE_SECONDARY_KEY * BORDER_SPACE_SECONDARY_AMOUNT

######

TUPLE_HEADER_EXECUTION_ANALYSIS = Tuple[str, str, str, str, str, str]
TUPLE_INTERPRETABLE_DATA = Tuple[str, str, str, str, str, str, str]


class DataContainerInterpretable:
    """
    A struct

    """

    def __init__(self, interpretable: Interpretable):
        self.interpretable = interpretable

        #####

        self.execution_index_relative = self.interpretable.get_execution_index_relative()

        self.trace_call_result: TraceCallResult = self.interpretable.get_trace_call_result_primary()

        self.line_number: int = self.trace_call_result.get_code_line_number()

        self.indent_depth_by_scope: int = self.interpretable.get_scope_parent().get_indent_depth_scope()

        self.indent_level: int = self.trace_call_result.get_indent_depth_corrected()

        self.spacing: int
        self.code: int
        self.spacing, self.code = self.trace_call_result.get_spacing_corrected_and_line()

        self.dict_k_variable_v_value: dict = interpretable.get_dict_k_variable_v_value()

        self.str_dict_k_variable_v_value: str = (
            str(self.dict_k_variable_v_value) if self.dict_k_variable_v_value else ""
        )

        self.list_str_comment = self.interpretable.get_list_str()

        self.str_list_str_comment = str(self.list_str_comment) if self.list_str_comment else ""


    def get_tuple_interpretable_data(self) -> TUPLE_INTERPRETABLE_DATA:

        return ( interpretable.get_execution_index_relative(),
                 line_number,
                 indent_depth_by_scope,
                 indent_level,
                 interpretable.get_execution_count(),
                 code,
                 dict_k_variable_v_value, )

class Style(Enum):
    COLORAMA = "colorama"
    RICH = "rich"

    def __eq__(self, other):
        """
        Override == for simplicity when comparing objects
        :param other:
        :return:
        """
        if isinstance(other, Style):
            return super().__eq__(other)
        elif isinstance(other, str):
            return self.value == other.lower()

        return self.value == other


STYLES = Literal[Style.COLORAMA, Style.RICH, None]


class CodeAnalyzerPrinter:

    def __init__(self, code_analyzer: _code_analyzer.CodeAnalyzer):
        self.code_analyzer: _code_analyzer.CodeAnalyzer = code_analyzer

        self.console = Console(
            soft_wrap=True,
            record=True,

        )

    def print(self, print_function: Callable = print, style: STYLES = Style.COLORAMA):
        """
        :param style:
        :param print_function:
        :return:
        """
        header = "{}\n{}\n{}\n".format(BORDER_SPACE_PRIMARY, "*** CODE ANALYSIS ***", BORDER_SPACE_PRIMARY)

        str_full = "{}\n{}\n\n{}".format(
            header,
            self.get_str_execution_analysis(style),
            self.get_str_line_of_code_analysis(style),
        )

        print_function(str_full)

        x = Text("This aa")
        x.stylize("red")
        z = Text("FFF") + x
        z.stylize("blue")

        # self.console.print(z)
        #
        # self.console.log("[red]This[/]")
        # self.console.print("[red]This[/]")
        # self.console.print("[blue underline]Looks like a link")

    def print_rich(self):

        table = Table(
            title="DATA YA",
            expand=True,
            # width=500
        )
        for i, column_name in enumerate(self._get_data_execution_analysis_column_names()):
            table.add_column(
                column_name,
                no_wrap=True,
            )

            # Doesn't work as intended
            # if i == 5:
            #     table.add_column(
            #         column_name,
            #         no_wrap=True,
            #         style=Syntax.get_theme("python").get_style_for_token()
            #     )
            # else:
            #     table.add_column(
            #         column_name,
            #         no_wrap=True,
            #     )

        # list_row: Generator[TUPLE_INTERPRETABLE_DATA] = (
        #     _get_data_execution_analysis_interpretable(interpretable, None) for interpretable in
        #     self.code_analyzer.list_interpretable if interpretable.visibility is True
        # )

        for interpretable in self.code_analyzer.list_interpretable:

            if interpretable.visibility is False:
                continue

            trace_call_result = interpretable.get_trace_call_result_primary()

            data_container_interpretable = DataContainerInterpretable(interpretable)

            """
            Notes:
                what the variable "list_str_data" contains can be found at the function
                self._get_data_execution_analysis_column_names 
                
                Notes:
                    list_str_data[0]  # 
                    list_str_data[1]
                    list_str_data[2]
                    list_str_data[3]
                    list_str_data[4]
                    list_str_data[5]
            """
            # Force all items to string or rich won't work
            list_str_data = [str(item) for item in data_container_interpretable]

            _str_dict_k_variable_v_value = list_str_data.pop()

            if _str_dict_k_variable_v_value:
                _str_dict_k_variable_v_value = "  {}".format(_str_dict_k_variable_v_value)

            """
            Notes:
                Styles for "style" can be found at https://rich.readthedocs.io/en/stable/style.html 
                Colors for "style" can be found at https://rich.readthedocs.io/en/stable/appendix/colors.html
            """
            _str_dict_k_variable_v_value_styled = Text(
                _str_dict_k_variable_v_value,
                style="rgb(255,0,0)",  # Red
                # style="dark_orange",
            )

            self.console.print(_str_dict_k_variable_v_value_styled)

            r"""
            Notes:
                Themes:
                    Possible themes for "theme" can be found at:
                        .../Lib/site-packages/rich/syntax.py
                    Look for the dict STYLE_MAP
                    
                    To see the style go to https://pygments.org/styles/
                    
                    Example:
                        theme="native"
                        theme="monokai"  # Which is the default
                
                The first arg in Syntax(...) is ignored when using highlight and there
                is no official documentation for highlight online. 
            """
            line: Text = Syntax("", lexer="python", theme="monokai").highlight(list_str_data[5])
            line.rstrip()

            ##########

            if (trace_call_result.get_python_keyword() == constants.Keyword.DEF and
                    trace_call_result.get_event() == constants.Event.LINE):
                line.stylize("on rgb(0,0,135)")  # Dark blue

            elif (trace_call_result.get_python_keyword() == constants.Keyword.DEF and
                  trace_call_result.get_event() == constants.Event.CALL):
                line.stylize("on rgb(0,95,0)")  # Dark green

            elif (trace_call_result.get_python_keyword() == constants.Keyword.CLASS and
                  trace_call_result.get_event() == constants.Event.LINE):
                line.stylize("on rgb(0,175,135)")  # Dark cyan

            # Fallback color for all Event.CALL
            elif trace_call_result.get_event() == constants.Event.CALL:
                line.stylize("on rgb(0,95,0)")  # Dark green

            ##########

            line.append(_str_dict_k_variable_v_value_styled)

            list_str_data[5] = line  # Recall that list_str_data[5] is the code with no style

            self.console.print(list_str_data[5])
            table.add_row(*list_str_data)
            self.console.print("FUCK", self.console.size)

        self.console.print(table)
        self.console.save_html("tet.html")

    def print_debug(self):
        """
        A debugging print_function used to figure out where bugs are

        :return:
        """

        print("{}\n{}\n{}\n".format(BORDER_SPACE_PRIMARY, "DEBUG PRINT", BORDER_SPACE_PRIMARY))

        for _inter in self.code_analyzer.list_interpretable:
            for _tra in _inter.list_trace_call_result:
                print(_tra, _tra.get_event())
            print()

    def _get_data_execution_analysis_column_names(self) -> TUPLE_HEADER_EXECUTION_ANALYSIS:

        column_names = ("Execution Index",
                        "Line #",
                        "Scope depth",
                        "Indent depth",
                        "Execution Count",
                        "Code + {Variable: Value}")

        return column_names

    def get_str_execution_analysis(self, style: STYLES = None) -> str:

        str_header_main: str = "{}\n{}\n{}\n".format(BORDER_SPACE_SECONDARY, "Execution Analysis",
                                                     BORDER_SPACE_SECONDARY)

        str_column_names: str = _get_str_execution_analysis(*self._get_data_execution_analysis_column_names(), "")

        generator_row: Generator[str] = (
            _get_str_execution_analysis_interpretable(interpretable, style) for
            interpretable in self.code_analyzer.list_interpretable if interpretable.visibility is True
        )

        str_full = "{}\n{}\n{}".format(
            str_header_main,
            str_column_names,
            "\n".join(generator_row)
        )

        return str_full

    def get_str_line_of_code_analysis(self, style: STYLES = None) -> str:
        """

        Notes:
            Recall that interpretables in self.code_analyzer.dict_k_interpretable_v_list_interpretable
            are grouped by .get_trace_call_result_primary call's
        :return:
        """
        str_header: str = "{}\n{}\n{}\n".format(BORDER_SPACE_SECONDARY, "Line of code Analysis", BORDER_SPACE_SECONDARY)

        list_str_information_full: List[str] = []

        for interpretable, list_interpretable in self.code_analyzer.dict_k_interpretable_v_list_interpretable.items():
            trace_call_result = interpretable.get_trace_call_result_primary()

            line_of_code = trace_call_result.code_line_strip

            filename_full = trace_call_result.filename_full

            line_number = trace_call_result.get_code_line_number()

            count = len(list_interpretable)

            # WARNING: dict_k_variable_v_value VARIES PER INTERPRETABLE, BUT
            dict_k_variable_v_value = interpretable.get_dict_k_variable_v_value()

            _filename_full_header = "File: "
            _line_number_header = "Line number: "
            _line_of_code_header = "Line of Code: "
            _line_of_code_body = line_of_code
            _count_header = "Count: "

            if style == Style.COLORAMA:
                _filename_full_header = colorama.Fore.MAGENTA + _filename_full_header + colorama.Style.RESET_ALL
                _line_of_code_header = colorama.Fore.GREEN + _line_of_code_header + colorama.Style.RESET_ALL
                _line_of_code_body = colorama.Fore.RED + line_of_code + colorama.Style.RESET_ALL
                _count_header = colorama.Fore.BLUE + _count_header + colorama.Style.RESET_ALL

            str_header_body = "{}{}\n{}{}\n{}{}\n{}{}".format(
                _filename_full_header,
                filename_full,
                _line_number_header,
                line_number,
                _line_of_code_header,
                _line_of_code_body,
                _count_header,
                count,
            )

            list_str_information_full.append(str_header_body)

            dict_body = {
                "Execution Index": (_interpretable.get_execution_index_relative() for _interpretable in
                                    list_interpretable),

                "Scope Depth": (_interpretable.get_scope_parent().get_indent_depth_scope() for _interpretable in
                                list_interpretable),

                "Execution Count": (_interpretable.get_execution_count() for _interpretable in
                                    list_interpretable),

                "{Key: Value} Pairs": (_interpretable.dict_k_variable_v_value for _interpretable in
                                       list_interpretable),
            }

            df_information = pd.DataFrame.from_dict(dict_body)

            # df_information.index.name = "Index"

            with pd.option_context('display.max_rows', None, ):
                list_str_information_full.append(df_information.to_string())

            list_str_information_full.append("\n")

        str_full = "{}\n{}\n".format(
            str_header,
            "\n".join(list_str_information_full),
        )

        return str_full

    def export_to_txt(self):
        print(os.path.basename(__file__))
        print(sys.argv[0])

        print(os.path.basename(sys.argv[0]))

        basename = os.path.basename(sys.argv[0])
        basename_no_ext = os.path.splitext(basename)[0]

        output_name = f"{basename_no_ext}_execution_analysis.txt"

        with open(output_name, "w") as file:
            self.print(print_function=file.write, style=None)


def _get_data_execution_analysis_interpretable(interpretable: Interpretable,
                                               style: STYLES = None) -> TUPLE_INTERPRETABLE_DATA:
    """
    Get data associated with a given interpretable

    :param interpretable:
    :return:
    """
    trace_call_result = interpretable.get_trace_call_result_primary()

    #####

    line_number = trace_call_result.get_code_line_number()

    indent_depth_by_scope = interpretable.get_scope_parent().get_indent_depth_scope()

    indent_level = trace_call_result.get_indent_depth_corrected()

    code = _get_str_trace_call_result_code(trace_call_result, style)

    #####

    dict_k_variable_v_value = interpretable.get_dict_k_variable_v_value()

    dict_k_variable_v_value = dict_k_variable_v_value if dict_k_variable_v_value else ""

    ##########

    return (
        interpretable.get_execution_index_relative(),
        line_number,
        indent_depth_by_scope,
        indent_level,
        interpretable.get_execution_count(),
        code,
        dict_k_variable_v_value,
    )


def _get_str_execution_analysis_interpretable(interpretable: Interpretable, style: STYLES = None) -> str:
    """
    Given an Interpretable, get a formatted string used for execution analysis

    :param interpretable:
    :param colored:
    :return:
    """

    return _get_str_execution_analysis(
        *_get_data_execution_analysis_interpretable(interpretable, style),
        style
    )


def _get_str_execution_analysis(execution_index,
                                line_number,
                                depth_scope,
                                indent_level,
                                execution_number_relative,
                                code,
                                dict_k_variable_v_value,
                                style: STYLES = None,
                                ) -> str:
    """
        Helper function for _get_str_execution_analysis_interpretable

    :param execution_index:
    :param line_number:
    :param depth_scope:
    :param indent_level:
    :param execution_number_relative:
    :param code:
    :param dict_k_variable_v_value:
    :param colored:
    :return:
    """
    if style == Style.COLORAMA:  # TODO ADD COLOR CODE CHANGE HERE
        _dict_k_variable_v_value = colorama.Fore.RED + str(dict_k_variable_v_value) + colorama.Style.RESET_ALL
    else:
        _dict_k_variable_v_value = dict_k_variable_v_value

    string = PRINT_FORMAT_STR_EXECUTION_ANALYSIS.format(
        execution_index,
        line_number,
        depth_scope,
        indent_level,
        execution_number_relative,
        code,
        _dict_k_variable_v_value
    )

    return string


def _get_str_trace_call_result_code(trace_call_result: TraceCallResult, style: STYLES = None) -> str:
    """
    Given a TraceCallResult, return a colored version of its __str__()

    :param code:
    :return:
    """
    spacing, line = trace_call_result.get_spacing_corrected_and_line()

    if style == Style.COLORAMA:

        color_fore: Union[str, colorama.Fore] = ""
        color_back: Union[str, colorama.Back] = ""

        if (trace_call_result.get_python_keyword() == constants.Keyword.DEF and
                trace_call_result.get_event() == constants.Event.LINE):
            color_fore = colorama.Fore.BLUE

        elif (trace_call_result.get_python_keyword() == constants.Keyword.DEF and
              trace_call_result.get_event() == constants.Event.CALL):
            color_fore = colorama.Fore.GREEN

        elif (trace_call_result.get_python_keyword() == constants.Keyword.CLASS and
              trace_call_result.get_event() == constants.Event.LINE):
            color_fore = colorama.Fore.CYAN

        # Fallback color for all Event.CALL
        elif trace_call_result.get_event() == constants.Event.CALL:
            color_fore = colorama.Fore.GREEN

        return spacing + color_fore + color_back + line + colorama.Style.RESET_ALL

    return spacing + line
