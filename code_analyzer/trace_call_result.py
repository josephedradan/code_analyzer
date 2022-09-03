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

from code_analyzer import interpretable as _interpretable
from code_analyzer.constants import Event, Keyword

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
                 ):
        """

        :param frame: Python Frame
        """
        self.frame: FrameType = frame

        self.event: str = event

        self.arg: str = arg  # Can be the argument returned from a callable call

        #####

        self.scope_depth_offset: int = 0

        ####################

        self.interpretable: Union[_interpretable.Interpretable, None] = None

        ####################

        """
        Frame related stuff
        """

        self.filename_raw: str = self.frame.f_code.co_filename

        self.path_object: Path = Path(self.filename_raw)
        # print("ABS FILE PATH", self.path_object.absolute())

        self.filename: str = self.path_object.name

        self.code_name: str = self.frame.f_code.co_name

        self.code_line_number: int = self.frame.f_lineno

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
        self.level_by_code_execution: int = self._get_scope_indent_level_by_line_spaces(self.code_line_spaces_pre)

    def assign_interpretable(self, interpretable: _interpretable.Interpretable):
        """
        Assign the interpretable that this object is apart of
        """
        self.interpretable = interpretable

    def get_indent_level_by_code_execution(self) -> int:
        """
        Indent level based on code execution

        """
        return self.level_by_code_execution

    def get_indent_level_relative_to_scope(self) -> int:
        """
        Indent level relative to the scope that the interpretable is one

        """
        if not self.interpretable:
            return 0

        return self.interpretable.scope_parent.get_indent_level_relative_to_scope(self)

    def get_indent_level_corrected(self) -> int:
        """
        Indent level relative ot the scope_parent

        Notes:
            Will shift the indent level by code execution

        """

        ####################
        # DEBUGGING START
        ####################

        # print("LEVEL BY EXECUTION: {}\n"
        #       "RELATIVE: {}\n"
        #       "START: {}\n"
        #       "CORRECTED (START + RELATIVE): {}\n"
        #       "OFFSET: {}".format(self.get_indent_level_by_code_execution(),
        #                           self.interpretable.scope_parent.get_indent_level_relative_to_scope(self),
        #                           self.interpretable.scope_parent.get_indent_level_first(),
        #                           (
        #                                   self.interpretable.scope_parent.get_indent_level_first() +
        #                                   self.interpretable.scope_parent.get_indent_level_relative_to_scope(self)
        #                           ),
        #                           self.scope_depth_offset
        #                           )
        #       )

        ####################
        # DEBUGGING END
        ####################
        return (
                self.interpretable.scope_parent.get_indent_level_first() +
                self.interpretable.scope_parent.get_indent_level_relative_to_scope(self) +
                self.scope_depth_offset
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
    def _get_scope_indent_level_by_line_spaces(line_spaces: str) -> int:
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
            # print("KEY WORD", match_1)
            return match_1[0].strip()
        elif match_2 is not None:
            # print("KEY WORD", match_2)
            return match_2[0].strip()

        return None

    def get_python_key_word(self) -> Union[Keyword, None]:
        if self.python_key_word is None:
            return None

        return Keyword(self.python_key_word)

    def get_event(self) -> Event:
        return Event(self.event)

    def set_scope_indent_level_offset(self, value: int):
        """
        Set an additional indent level offset
        """
        self.scope_depth_offset = value

    def __str__(self):
        """

        Notes:
            self.code_object.co_filename  The filename
            self.code_object.co_freevars  The closure variables
            self.code_object.co_name      Name of the callable that the the line of code is inside of

        :return:
        """

        result = "{}{}".format(
            self.get_indent_level_corrected() * _PYTHON_INDENT_SPACE_AMOUNT * ' ',
            self.code_line_clean,
        )

        return result

    def __hash__(self):
        return hash((self.filename_raw, self.code_line_number))

    def __eq__(self, other):
        return self.__hash__()