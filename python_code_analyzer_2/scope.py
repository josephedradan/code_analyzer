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

from python_code_analyzer_2.trace_call_result import TraceCallResult


# # __slots__ = ["scope_level_by_code_execution", "scope_container_parent", "velocity"]
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
                 scope_level_by_code_execution: int = 0,
                 scope_level_by_analyzer: int = 0,
                 scope_container_parent: Union[Scope, None] = None
                 ):
        """

        :param scope_level_by_code_execution: INDENT LEVEL
        :param scope_level_by_analyzer:
        :param scope_container_parent:
        """

        self.scope_level_by_code_execution: int = scope_level_by_code_execution

        self.scope_depth: int = scope_level_by_analyzer  # HOW DEEP THE SCOPE IS, THIS IS UNRELATED TO EVERYTHING ELSE

        self.scope_container_parent: Union[Scope, None] = scope_container_parent

        ##########

        self.list_trace_call_result: List[TraceCallResult] = []

        ####################
        self._scope_level_difference = 0




    def add_trace_call_result(self, trace_call_result: TraceCallResult):
        """

        Notse:
            1. Adds to list of trace_call_results
            2. Assigns scope level corrected to the given trace_call_result
        :param trace_call_result:
        :return:
        """

        if not self.list_trace_call_result:
            self._scope_level_difference = self.scope_level_by_code_execution - trace_call_result.get_scope_level_by_code()
            print("SCOPE LEVEL BY CODE", trace_call_result.get_scope_level_by_code(), self.list_trace_call_result)
            print("STARTING", self.scope_level_by_code_execution)
        self._assign_level_scope_correct(trace_call_result)

        self.list_trace_call_result.append(trace_call_result)

    def _assign_level_scope_correct(self, trace_call_result: TraceCallResult):
        scope_level_correct = trace_call_result.get_scope_level_by_code() + self._scope_level_difference

        from joseph_library.print import print_color, print_green, print_cyan
        print_cyan(f"DIFF { self._scope_level_difference}")
        print_green(f"BY CODE {trace_call_result.get_scope_level_by_code()}")
        print_color.f_red().print(f"CORRECTED LEVEL: {scope_level_correct}")

        trace_call_result.set_scope_level_corrected(scope_level_correct)

    def get_list_trace_call_result(self) -> List[TraceCallResult]:
        return self.list_trace_call_result

    def get_trace_call_result_top(self) -> Union[TraceCallResult, None]:
        if self.list_trace_call_result:
            return self.list_trace_call_result[-1]

        return None

    def pop(self):
        return self.list_trace_call_result.pop()
