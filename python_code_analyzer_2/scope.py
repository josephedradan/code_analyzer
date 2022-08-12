"""
Created by Joseph Edradan
Github: https://github.com/josephedradan

Date created: 6/25/2022

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

from typing import Union, List

from python_code_analyzer_2 import interpretable
from python_code_analyzer_2 import trace_call_result


# # __slots__ = ["indent_level_start", "scope", "velocity"]
#
# """
#
# Notes:
#     Lightweight container class to contain specific things.
#     __slots__ will prevent additional attribute creation.
#     // Property decorator will prevent attribute assignment.
#
# """


class Scope:
    def __init__(self,
                 indent_level_start: int = 0,
                 depth_by_analyzer: int = 0,
                 scope_parent: Union[Scope, None] = None
                 ):
        """

        :param indent_level_start: INDENT LEVEL
        :param depth_by_analyzer:
        :param scope_parent:
        """

        # Starting index depth of where to place the code
        self.indent_level_start: int = indent_level_start

        # Depth that is custom
        self.depth_by_analyzer: int = depth_by_analyzer  # HOW DEEP THE SCOPE IS, THIS IS UNRELATED TO EVERYTHING ELSE

        # Parent Scope
        self.scope_parent: Union[Scope, None] = scope_parent

        ####################

        self.list_interpretable: List[interpretable.Interpretable] = []

        ####################

    def _get_first_trace_call_result(self) -> Union[trace_call_result.TraceCallResult, None]:
        if self.list_interpretable:
            list_trace_call_result = self.list_interpretable[0].get_list_trace_call()
            return list_trace_call_result[0]

    def _get_index_level_relative(self,
                                  trace_call_result_primary: trace_call_result.TraceCallResult,
                                  trace_call_result_secondary: trace_call_result.TraceCallResult):
        return (
                trace_call_result_secondary.get_indent_level_by_code_execution() -
                trace_call_result_primary.get_indent_level_by_code_execution()
        )

    def _add_interpretable(self, interpretable: interpretable.Interpretable) -> None:
        self.list_interpretable.append(interpretable)

    def pop_interpretable(self) -> Union[interpretable.Interpretable, None]:
        if self.list_interpretable:
            return self.list_interpretable.pop()

        return None

    def get_index_level_relative(self, trace_call_result_given: trace_call_result.TraceCallResult):

        trace_call_result_first = self._get_first_trace_call_result()

        if trace_call_result_first:
            return self._get_index_level_relative(
                trace_call_result_first,
                trace_call_result_given
            )
        return 0

    def get_index_level_start(self) -> int:

        trace_call_result_first = self._get_first_trace_call_result()

        if trace_call_result_first:
            return self.indent_level_start

        return 0

        # if self.list_interpretable:
        #     list_trace_call_result = self.list_interpretable[0].get_list_trace_call()
        #     # print(self)
        #     # print(self.list_interpretable)
        #
        #     if list_trace_call_result:
        #         trace_call_result_first = list_trace_call_result[0]
        #         print(
        #             f"START DEPTH {self.indent_level_start}, GET LEVEL BY EXE {trace_call_result_first.get_indent_level_by_code_execution()} LEVEL OFFSET: {self.indent_level_start - trace_call_result_first.get_indent_level_by_code_execution()}")
        #         # print(f"GET LEVEL BY EXE {trace_call_result_first.get_indent_level_by_code_execution()}")
        #
        #         # Assign the offset
        #         return (
        #                 self.indent_level_start -
        #                 trace_call_result_first.get_indent_level_by_code_execution()
        #         )
        #
        # return 0

    # TODO DELETE
    # def set_list_trace_call_result(self, list_interpretable: List[trace_call_result.TraceCallResult]):
    #     self.list_interpretable = list_interpretable

    def assign_trace_call_result_level_scope_correct(self, trace_call_result: trace_call_result.TraceCallResult):
        """

        Notse:
            1. Adds to list of trace_call_results
            2. Assigns scope level corrected to the given trace_call_result
        :param trace_call_result:
        :return:
        """

        if not self.list_interpretable:
            self._scope_level_offset_pseudo = self.indent_level_start - trace_call_result.get_indent_level_by_code_execution()
            print("SCOPE LEVEL BY CODE", trace_call_result.get_indent_level_by_code_execution(),
                  self.list_interpretable)
            print("STARTING", self.indent_level_start)

        self._assign_level_scope_correct(trace_call_result)

    def _assign_level_scope_correct(self, trace_call_result: trace_call_result.TraceCallResult):
        scope_level_correct = trace_call_result.get_indent_level_by_code_execution() + self._scope_level_offset_pseudo

        from joseph_library.print import print_color, print_green, print_cyan
        print_cyan(f"DIFF {self._scope_level_offset_pseudo}")
        print_green(f"BY CODE {trace_call_result.get_indent_level_by_code_execution()}")
        print_color.f_red().print(f"CORRECTED LEVEL: {scope_level_correct}")

        trace_call_result.set_scope_level_corrected(scope_level_correct)

    # def get_list_trace_call_result(self) -> List[trace_call_result.TraceCallResult]:
    #     return self.list_interpretable
    #

    def get_interpretable_top(self) -> Union[interpretable.Interpretable, None]:
        if self.list_interpretable:
            return self.list_interpretable[-1]

        return None


