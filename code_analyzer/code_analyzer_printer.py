"""
Created by Joseph Edradan
Github: https://github.com/josephedradan

Date created: 11/6/2022

Purpose:

Details:

Description:

Notes:

            Exe Index Rel:  Execution Index Relative to the start()
            Line #:         Line Number in code
            Scope depth:    Scope depth (How deep the scope is by index, it is based on a function's call)
            Indent depth:   Indent Level (How deep the indent is)
            Exe Count:      Execution Count (Count of how many times a unique line has been executed)


IMPORTANT NOTES:

Explanation:

Tags:

Reference:

"""

from __future__ import annotations

from typing import List

import colorama
import pandas as pd

import code_analyzer as _code_analyzer
from code_analyzer.interpretable import Interpretable

PRINT_FORMAT = "{:<16}{:<10}{:<14}{:<14}{:<16}{} {}"


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

        print("{}\n{}\n{}\n".format("#" * 100, "*** CODE ANALYSIS ***", "#" * 100))

        ########################################

        print("{}\n{}\n{}\n".format("-" * 50, "Execution Analysis", "-" * 50))

        colorama.init()

        print(_get_execution_analysis_string("Exe Index Rel", "Line #", "Scope depth", "Indent depth", "Exe Count",
                                             "Code + {Variable: Value}",
                                             ""))
        for interpretable in self.code_analyzer.list_interpretable:
            print(_get_execution_analysis_string_interpretable(interpretable))

        ########################################
        # FUCK

        for _inter in self.code_analyzer.list_interpretable:
            for _tra in _inter.list_trace_call_result:
                print(_tra, _tra.get_event())
            print()
        # FUCK
        ###
        print("\n{}\n{}\n{}\n".format("-" * 50, "Line Analysis", "-" * 50))

        list_interpretable: List[Interpretable]
        for interpretable, list_interpretable in self.code_analyzer.dict_k_interpretable_v_list_interpretable.items():
            trace_call_result = interpretable.get_trace_call_result_primary()

            line_of_code = trace_call_result.code_line_strip

            filename_full = trace_call_result.filename_full

            count = len(list_interpretable)

            print("\nLine of Code: {}\nFile: {}\nCount: {}".format(line_of_code, filename_full, count))

            generator_information = ((
                _interpretable.get_execution_index_relative(),
                _interpretable.get_scope_parent().get_indent_depth_scope(),
                _interpretable.get_execution_count(),
                _interpretable.dict_k_variable_v_value
            ) for _interpretable in list_interpretable)

            df_information = pd.DataFrame(
                generator_information,
                columns=["Execution Index Relative",
                         "Scope Depth",
                         "Execution Count",
                         "{Key: Value} Pairs"])
            with pd.option_context('display.max_rows', None, ):
                print(df_information.to_string())

            print("\n-----")


def _get_execution_analysis_string_interpretable(interpretable: Interpretable):
    trace_call_result = interpretable.get_trace_call_result_primary()

    #####

    line_number = trace_call_result.get_code_line_number()

    indent_depth_by_scope = interpretable.get_scope_parent().get_indent_depth_scope()

    indent_level = trace_call_result.get_indent_depth_corrected()

    code = str(trace_call_result)

    #####

    dict_k_variable_v_value = interpretable.get_dict_k_variable_v_value()
    dict_k_variable_v_value = dict_k_variable_v_value if dict_k_variable_v_value else ""

    ##########

    return _get_execution_analysis_string(
        interpretable.get_execution_index_relative(),
        line_number,
        indent_depth_by_scope,
        indent_level,
        interpretable.get_execution_count(),
        code,
        dict_k_variable_v_value
    )


def _get_execution_analysis_string(execution_index,
                                   line_number,
                                   depth_scope,
                                   indent_level,
                                   execution_number_relative,
                                   code,
                                   dict_k_variable_v_value
                                   ):
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
