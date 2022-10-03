"""
Created by Joseph Edradan
Github: https://github.com/josephedradan

Date created: 6/25/2022

Purpose:

Details:

Description:

Notes:
    On the subject of potentially using __slots__
        Lightweight container class to contain specific things.
        __slots__ will prevent additional attribute creation.
        // Property decorator will prevent attribute assignment.

IMPORTANT NOTES:

Explanation:

Tags:

Reference:

"""
from __future__ import annotations

from typing import Union, List

from code_analyzer import interpretable
from code_analyzer import trace_call_result


class Scope:
    def __init__(self,
                 indent_depth_start: int = 0,
                 indent_depth_by_scope: int = 0,
                 scope_parent: Union[Scope, None] = None
                 ):
        """
        :param indent_depth_start:
        :param indent_depth_by_scope:
        :param scope_parent:
        """

        # Starting indent level to place the code
        self.indent_depth_start: int = indent_depth_start

        # Depth that is custom
        self.indent_depth_by_scope: int = indent_depth_by_scope  # HOW DEEP THE SCOPE IS, THIS IS UNRELATED TO EVERYTHING ELSE

        # Parent Scope
        self.scope_parent: Union[Scope, None] = scope_parent

        ####################

        self.list_interpretable: List[interpretable.Interpretable] = []

    def get_indent_depth_by_scope(self) -> int:
        return self.indent_depth_by_scope

    def get_scope_parent(self) -> Union[Scope, None]:
        return self.scope_parent

    def _get_trace_call_result_first(self) -> Union[trace_call_result.TraceCallResult, None]:
        """
        Get first TraceCallResult

        :return:
        """
        if self.list_interpretable:
            list_trace_call_result = self.list_interpretable[0].get_list_trace_call()
            return list_trace_call_result[0]

    @staticmethod
    def _get_indent_level_relative(trace_call_result_primary: trace_call_result.TraceCallResult,
                                   trace_call_result_secondary: trace_call_result.TraceCallResult):
        """
        Helper function for get_indent_level_relative_to_scope

        :param trace_call_result_primary:
        :param trace_call_result_secondary:
        :return:
        """
        return (
                trace_call_result_secondary.get_indent_level_by_code_execution() -
                trace_call_result_primary.get_indent_level_by_code_execution()
        )

    def add_interpretable(self, interpretable: interpretable.Interpretable) -> None:
        self.list_interpretable.append(interpretable)

    def pop_interpretable(self) -> Union[interpretable.Interpretable, None]:
        if self.list_interpretable:
            return self.list_interpretable.pop()

        return None

    def get_indent_level_relative_to_scope(self, trace_call_result_given: trace_call_result.TraceCallResult):
        """
        Get the corrected indent level for the given TraceCallResult

        Notes:
            This function does not care if the given TraceCallResult is not relative to this scope

        :param trace_call_result_given:
        :return:
        """
        trace_call_result_first = self._get_trace_call_result_first()

        if trace_call_result_first:
            return self._get_indent_level_relative(
                trace_call_result_first,
                trace_call_result_given
            )
        return 0

    def get_indent_level_first(self) -> int:
        """
        Get the indent level of the first TraceCallResult

        """
        trace_call_result_first = self._get_trace_call_result_first()

        if trace_call_result_first:
            return self.indent_depth_start

        return 0

    def get_interpretable_top(self) -> Union[interpretable.Interpretable, None]:
        """
        Get the most recently added interpretable
        """
        if self.list_interpretable:
            return self.list_interpretable[-1]

        return None

    def get_interpretable(self, index) -> Union[interpretable.Interpretable, None]:
        try:
            return self.list_interpretable[index]
        except IndexError as e:
            return None
