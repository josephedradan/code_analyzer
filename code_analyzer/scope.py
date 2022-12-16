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

from typing import Union, List, Iterable, Set

from code_analyzer import interpretable
from code_analyzer import trace_call_result


class Scope:
    def __init__(self,
                 scope_parent: Union[Scope, None] = None,
                 indent_depth_offset: int = 0
                 ):
        """
        :param scope_parent: Parent scope if it exists
        :param indent_depth_offset: Additional depth
        """

        # Offset Scope depth
        self.indent_depth_offset: int = indent_depth_offset

        # Parent Scope
        self.scope_parent: Union[Scope, None] = scope_parent

        ####################

        self.list_interpretable: List[interpretable.Interpretable] = []

        ####################

        self.set_variable_exclusion: Set[str] = set()

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

        return None

    def add_interpretable(self, interpretable: interpretable.Interpretable) -> None:
        self.list_interpretable.append(interpretable)

    def pop_interpretable(self) -> Union[interpretable.Interpretable, None]:
        if self.list_interpretable:
            return self.list_interpretable.pop()

        return None

    @staticmethod
    def _get_indent_depth_relative(trace_call_result_primary: trace_call_result.TraceCallResult,
                                   trace_call_result_secondary: trace_call_result.TraceCallResult):
        """
        Helper function for get_indent_level_relative_to_scope

        :param trace_call_result_primary:
        :param trace_call_result_secondary:
        :return:
        """

        return (
                trace_call_result_secondary.get_indent_depth_by_code_execution() -
                trace_call_result_primary.get_indent_depth_by_code_execution()
        )

    def get_indent_depth_relative_to_scope(self, trace_call_result_given: trace_call_result.TraceCallResult):
        """
        Get the corrected indent level for the given TraceCallResult

        Notes:
            This function does not care if the given TraceCallResult is not relative to this scope

        :param trace_call_result_given:
        :return:
        """
        trace_call_result_first = self._get_trace_call_result_first()

        if trace_call_result_first:
            return self._get_indent_depth_relative(
                trace_call_result_first,
                trace_call_result_given
            )

        return 0

    def get_indent_depth_corrected(self) -> int:
        """
        Get the indent depth based on:
            Parent Scope indent depth corrected +
            1 +
            this object's indent depth offset

        Notes:
            This indent depth should be used for visual purposes

        :return:
        """
        if self.scope_parent is None:
            return 0

        return self.scope_parent.get_indent_depth_corrected() + 1 + self.indent_depth_offset

    def get_indent_depth_scope(self) -> int:
        """
        Get the scope indent depth:
            Parent Scope indent depth + 1

        Notes:
            This is the actual indent depth of this scope

        :return:
        """
        if self.scope_parent is None:
            return 0

        return self.scope_parent.get_indent_depth_scope() + 1

    def get_indent_depth_interpretable_first(self) -> int:
        """
        Get the indent depth of the first TraceCallResult

        """
        trace_call_result_first = self._get_trace_call_result_first()

        if trace_call_result_first:
            return self.get_indent_depth_corrected()

        return 0

    def get_interpretable_top(self) -> Union[interpretable.Interpretable, None]:
        """
        Get the most recently added interpretable
        """
        if self.list_interpretable:
            return self.list_interpretable[-1]

        return None

    def get_interpretable(self, index: Union[None, int] = None) -> Union[interpretable.Interpretable, None]:
        if index is None:
            return self.get_interpretable_top()

        try:
            return self.list_interpretable[index]
        except IndexError as e:
            return None

    def update_set_variable_exclusion(self, iterable_: Iterable):
        """

        :param iterable_:
        :return:
        """

        self.set_variable_exclusion.update(iterable_)

    def get_set_variable_exclusion(self) -> Set[str]:
        return self.set_variable_exclusion
