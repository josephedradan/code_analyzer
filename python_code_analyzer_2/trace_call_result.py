"""
Created by Joseph Edradan
Github: https://github.com/josephedradan

Date created: 6/7/2022

Purpose:
    A container file that holds information about trace_call_result python lines of code

    Example:

        Line example:
            for i in range(10):

        Will probably have the data:
            Line number
            Code
            FrameType
            CodeType
            Indent level


Details:

Description:

Notes:

IMPORTANT NOTES:

Explanation:

Tags:

Reference:

"""
from __future__ import annotations

import linecache
import re
from pathlib import Path
from types import FrameType, CodeType
from typing import Union

from python_code_analyzer_2 import interpretable
from python_code_analyzer_2.constants import Event, Keyword

_PYTHON_INDENT_SPACE_AMOUNT = 4
_PYTHON_INDENT_SPACES = _PYTHON_INDENT_SPACE_AMOUNT * " "

_PYTHON_KEY_WORD_REGEX_PATTERN = r"^\s*(and|as|assert|break|case|class|continue|def|del|elif|else|except|False|finally|for|from|global|if|import|in|is|lambda|match|None|nonlocal|not|or|pass|raise|return|True|try|while|with|yield)(\s+|\()"

_PYTHON_KEY_WORD_REGEX_PATTERN_NO_SPACE = r"^\s*(break|continue|False|None|pass|return|True|yield)$"


class TraceCallResult:
    """
    Basically, objects that are of this type are individual lines of python code that executed/interpreted.
    """

    def __init__(self,
                 frame: FrameType,
                 event: str,
                 arg: str,
                 indent_level_by_application: int,
                 indent_level_offset: int = 0
                 ):
        """

        :param frame: Python Frame
        :param level_scope: Scope level of the code being interpreted
        :param index_trace_call_result_line_number: index of the trace_call_result (code basically) based on line number
        :param index_trace_call_result_global: Global index of the trace_call_result (code basically)
        """
        self.frame: FrameType = frame

        self.event: str = event

        self.arg: str = arg  # Can be the argument returned from a callable call

        self.indent_level_by_application: int = indent_level_by_application

        self.indent_level_offset: int = indent_level_offset

        ####################

        # self.trace_call_result_previous_scope: [TraceCallResult, None] = None  # FIXME: THIS IS A LINKED LIST DESIGN

        # self.trace_call_result_previous_direct: [TraceCallResult, None] = None # FIXME: THIS IS A LINKED LIST DESIGN

        self.interpretable: Union[interpretable.Interpretable, None] = None

        ####################

        ####################
        """
        Frame related stuff
        """

        self.filename_raw: str = self.frame.f_code.co_filename

        self.path_object: Path = Path(self.filename_raw)
        # print("ABS FILE PATH", self.path_object.absolute())

        self.filename: str = self.path_object.name

        self.callable_name: str = self.frame.f_code.co_name

        self.callable_line_number: int = self.frame.f_lineno

        self.code_object: CodeType = self.frame.f_code

        # The line of code
        self.code_line = linecache.getline(str(self.path_object.absolute()), self.frame.f_lineno)

        ##########
        """
        Line of code related stuff
        """

        # The line of code (no new line        )
        self.code_line_rstrip = self.code_line.rstrip()

        self.code_line_clean = self.code_line.strip()

        self.code_line_spaces_pre = self._get_line_spaces_pre(self.code_line)

        ##########

        self.python_key_word = self._get_python_key_word(self.code_line_clean)

        ##########
        """
        Scope related stuff
        """

        # Frame level determined by counting spaces by the python's indent size
        self.level_by_code_execution: int = self._get_scope_level_by_line_spaces(self.code_line_spaces_pre)

        # print("CODE LINE", self.code_line)
        # print(self.code_line, end="")
        # print("#" * 50)

    def assign_interpretable(self, interpretable: interpretable.Interpretable):
        self.interpretable = interpretable

    # def set_scope_level_corrected(self, value):
    #     self._level_corrected = value

    # TODO DELETE
    # def get_scope_level_corrected(self):
    #     _scope_level_corrected = 0
    #     if self.event == constants.CALL and self.trace_call_result_previous:
    #         _scope_level_corrected = self.trace_call_result_previous._level_corrected
    #     elif self.trace_call_result_previous:
    #         _scope_level_corrected = (
    #                 self.scope_level_container.get_velocity() +
    #                 self.trace_call_result_previous._level_corrected
    #         )
    #
    #     return _scope_level_corrected

    def get_indent_level_by_code_execution(self) -> int:
        """
        Indent level based on code execution

        """
        return self.level_by_code_execution

    def get_indent_level_relative(self) -> int:
        return self.interpretable.scope.get_index_level_relative(self)

    def get_indent_level_corrected(self) -> int:
        """
        Indent level relative ot the scope

        Notes:
            Will shift the indent level by code execution

        """
        print("LEVEL BY EXECUTION:",
              self.get_indent_level_by_code_execution(),
              "RELATIVE",
              self.interpretable.scope.get_index_level_relative(self),
              "START",
              self.interpretable.scope.get_index_level_start(),
              " = CORRECTED",
              self.interpretable.scope.get_index_level_start() + self.interpretable.scope.get_index_level_relative(self),
              "| OFFSET IS",
              self.indent_level_offset
              )

        return (
                self.interpretable.scope.get_index_level_start() +
                self.interpretable.scope.get_index_level_relative(self) +
                self.indent_level_offset
        )

    @staticmethod
    def _get_line_spaces_pre(string_given: str) -> str:
        """
        Regex to get the spaces at the start of a given string

        :param string_given:
        :return:
        """
        match = re.match("^ +", string_given)

        if match is not None:
            return match[0]

        return ""

    @staticmethod
    def _get_scope_level_by_line_spaces(line_spaces: str) -> int:
        """
        Gets the python indent space amount in the given string

        IMPORTANT NOTES:
            THIS FUNCTION MAY OR MAY NOT CARE IF THE STRING ACTUALLY HAS SPACES OR NOT

        :param line_spaces:
        :return:
        """

        # amount_indent = len(re.findall(_PYTHON_INDENT_SPACES, line_spaces))
        # return amount_indent

        return int(len(line_spaces) // _PYTHON_INDENT_SPACE_AMOUNT)

    @staticmethod
    def _get_python_key_word(line: str) -> Union[str, None]:
        match_1 = re.match(_PYTHON_KEY_WORD_REGEX_PATTERN, line)
        match_2 = re.match(_PYTHON_KEY_WORD_REGEX_PATTERN_NO_SPACE, line)

        if match_1 is not None:
            print("KEY WORD", match_1)
            return match_1[0].strip()
        elif match_2 is not None:
            print("KEY WORD", match_2)
            return match_2[0].strip()

        return None

    def get_python_key_word(self) -> Union[Keyword, None]:
        if self.python_key_word is None:
            return None

        return Keyword(self.python_key_word)

    def get_event(self) -> Event:
        return Event(self.event)

    # TODO REMOVE
    # def get_scope_level_container_by_application(self) -> Scope:
    #     return self.scope_level_container
    #
    # def set_scope_level_by_application(self, value: int) -> None:
    #     self.scope_level_container = value

    # TODO DELETE
    # def set_trace_call_result_previous_by_scope(self, trace_call_result_previous: TraceCallResult):
    #     self.trace_call_result_previous_scope = trace_call_result_previous
    #
    # def get_trace_call_result_previous_by_scope(self) -> TraceCallResult:
    #     return self.trace_call_result_previous_scope
    #
    # def set_trace_call_result_previous_by_direct(self, trace_call_result_previous: TraceCallResult):
    #     self.trace_call_result_previous_direct = trace_call_result_previous
    #
    # def get_trace_call_result_previous_by_direct(self) -> TraceCallResult:
    #     return self.trace_call_result_previous_direct

    # def exhaust_list_dict_k_variable_v_value(self, list_dict_k_variable_v_value: List[Dict[str, Any]]) -> None:
    #     """
    #     Exhaust list_dict_k_variable_v_value_for_trace_call_result to the given trace_call_result
    #
    #     :param trace_call_result:
    #     :param list_dict_k_variable_v_value:
    #     :return:
    #     """
    #     # print(list_dict_k_variable_v_value)
    #     while list_dict_k_variable_v_value:
    #         self.dict_k_variable_v_value.update(list_dict_k_variable_v_value.pop())

    def set_indent_level_offset(self, value: int):
        self.indent_level_offset = value

    def __str__(self):
        """

        Notes:
            self.code_object.co_filename  The filename
            self.code_object.co_freevars  The closure variables
            self.code_object.co_name      Name of the callable that the the line of code is inside of

        :return:
        """
        # Debugging
        # for key in self.frame.f_locals:
        #     print(f"{self._scope_level_by_application * ' '}{key} "
        #           f"{type(self.frame.f_locals[key])} "
        #           f"{self.frame.f_locals[key]} "
        #           f"")

        # self.code_object.co_filename  The filename
        # self.code_object.co_freevars  The closure variables
        # self.code_object.co_name      Name of the callable that the code is within

        # if self.arg:
        #     raise Exception(f"JOSEPH LOOK AT THIS {self.arg}")

        return f"{self.get_indent_level_corrected() * _PYTHON_INDENT_SPACE_AMOUNT * ' '}{self.code_line_clean} ||| {self.event}"

        # return f"{self.get_indent_level_by_code_execution() * _PYTHON_INDENT_SPACE_AMOUNT * ' '}{self.code_line_clean} ||| {self.event}"

        ####

        # return f"{self._level_corrected * _PYTHON_INDENT_SPACE_AMOUNT * ' '}{self.code_line_clean} {self.event} {self.dict_k_variable_v_value} {self.code_object.co_freevars} {self.arg} {self.frame.f_locals.keys()} {self.frame.f_back}"
        # return f"{self.code_line_rstrip} {self.event} {self.dict_k_variable_v_value} {self.code_object.co_freevars} {self.arg} {self.frame.f_locals.keys()}"

        # return f"{self.get_indent_level_corrected() * _PYTHON_INDENT_SPACE_AMOUNT * ' '}{self.code_line_clean} {self.event} {self.dict_k_variable_v_value} {self.code_object.co_freevars} {self.arg} {self.frame.f_locals.keys()} {self.frame.f_back}"
