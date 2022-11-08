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

from typing import List, Union

import colorama
import pandas as pd

import code_analyzer as _code_analyzer
from code_analyzer import constants
from code_analyzer.interpretable import Interpretable
from code_analyzer.trace_call_result import TraceCallResult

PRINT_FORMAT = "{:<16}{:<10}{:<14}{:<14}{:<18}{} {}"

colorama.init()

BORDER_SPACE_PRIMARY_KEY = "#"
BORDER_SPACE_SECONDARY_KEY = "-"

BORDER_SPACE_PRIMARY_AMOUNT = 100
BORDER_SPACE_SECONDARY_AMOUNT = 50

BORDER_SPACE_PRIMARY = BORDER_SPACE_PRIMARY_KEY * BORDER_SPACE_PRIMARY_AMOUNT
BORDER_SPACE_SECONDARY = BORDER_SPACE_SECONDARY_KEY * BORDER_SPACE_SECONDARY_AMOUNT


class CodeAnalyzerPrinter:

    def __init__(self, code_analyzer: _code_analyzer.CodeAnalyzer):
        self.code_analyzer: _code_analyzer.CodeAnalyzer = code_analyzer

    def print(self):
        """
              Notes:
                  Exe Index Rel:  Execution Index Relative to the start()
                  Line #:         Line Number in code
                  Scope depth:    Scope depth (How deep the scope is by index, it is based on a function's call)
                  Indent depth:   Indent Level (How deep the indent is)
                  Exe Count:      Execution Count (Count of how many times a unique line has been executed)

              :return:
              """
        header = "{}\n{}\n{}\n".format(BORDER_SPACE_PRIMARY, "*** CODE ANALYSIS ***", BORDER_SPACE_PRIMARY)

        str_full = "{}\n{}\n\n{}".format(
            header,
            self.get_str_execution_analysis(),
            self.get_str_line_of_code_analysis(),
        )

        print(str_full)

    def print_debug(self):
        """
        A debugging print used to figure out where bugs are

        :return:
        """

        print("{}\n{}\n{}\n".format(BORDER_SPACE_PRIMARY, "DEBUG PRINT", BORDER_SPACE_PRIMARY))

        for _inter in self.code_analyzer.list_interpretable:
            for _tra in _inter.list_trace_call_result:
                print(_tra, _tra.get_event())
            print()

    def get_str_execution_analysis(self) -> str:
        str_header: str = "{}\n{}\n{}\n".format(BORDER_SPACE_SECONDARY, "Execution Analysis", BORDER_SPACE_SECONDARY)

        str_header_body: str = _get_str_execution_analysis("Execution Index",
                                                           "Line #",
                                                           "Scope depth",
                                                           "Indent depth",
                                                           "Execution Count",
                                                           "Code + {Variable: Value}",
                                                           "")

        list_body: List[str] = [_get_str_execution_analysis_interpretable(interpretable) for interpretable in
                                self.code_analyzer.list_interpretable]

        str_full = "{}\n{}\n{}".format(
            str_header,
            str_header_body,
            "\n".join(list_body)
        )

        return str_full

    def get_str_line_of_code_analysis(self) -> str:
        str_header: str = "{}\n{}\n{}\n".format(BORDER_SPACE_SECONDARY, "Line of code Analysis", BORDER_SPACE_SECONDARY)

        list_str_information_full: List[str] = []

        for interpretable, list_interpretable in self.code_analyzer.dict_k_interpretable_v_list_interpretable.items():
            trace_call_result = interpretable.get_trace_call_result_primary()

            line_of_code = trace_call_result.code_line_strip

            filename_full = trace_call_result.filename_full

            count = len(list_interpretable)

            str_header_body = "{}{}\n{}{}\n{}{}".format(
                colorama.Fore.MAGENTA + "File: " + colorama.Style.RESET_ALL,
                filename_full,
                colorama.Fore.GREEN + "Line of Code: " + colorama.Style.RESET_ALL,
                colorama.Fore.RED + line_of_code + colorama.Style.RESET_ALL,
                colorama.Fore.BLUE + "Count: " + colorama.Style.RESET_ALL,
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


def _get_str_execution_analysis_interpretable(interpretable: Interpretable) -> str:
    """
    Given an Interpretable, get a formatted string used for execution analysis

    :param interpretable:
    :return:
    """
    trace_call_result = interpretable.get_trace_call_result_primary()

    #####

    line_number = trace_call_result.get_code_line_number()

    indent_depth_by_scope = interpretable.get_scope_parent().get_indent_depth_scope()

    indent_level = trace_call_result.get_indent_depth_corrected()

    code = _get_str_trace_call_result_code_colored(trace_call_result)

    #####

    dict_k_variable_v_value = interpretable.get_dict_k_variable_v_value()
    dict_k_variable_v_value = dict_k_variable_v_value if dict_k_variable_v_value else ""

    ##########

    return _get_str_execution_analysis(
        interpretable.get_execution_index_relative(),
        line_number,
        indent_depth_by_scope,
        indent_level,
        interpretable.get_execution_count(),
        code,
        dict_k_variable_v_value
    )


def _get_str_execution_analysis(execution_index,
                                line_number,
                                depth_scope,
                                indent_level,
                                execution_number_relative,
                                code,
                                dict_k_variable_v_value
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
    :return:
    """
    string = PRINT_FORMAT.format(
        execution_index,
        line_number,
        depth_scope,
        indent_level,
        execution_number_relative,
        code,
        colorama.Fore.RED + str(dict_k_variable_v_value) + colorama.Style.RESET_ALL
    )

    return string


def _get_str_trace_call_result_code_colored(trace_call_result: TraceCallResult) -> str:
    """
    Given a TraceCallResult, return a colored version of its __str__()

    :param code:
    :return:
    """

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

    return color_fore + color_back + str(trace_call_result) + colorama.Style.RESET_ALL
