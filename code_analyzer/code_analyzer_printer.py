"""
Date created: 11/6/2022

Purpose:

Details:

Description:

Notes:

IMPORTANT NOTES:

Explanation:

Tags:

Contributors:
    https://github.com/josephedradan

Reference:

TODO:
    REDESIGN ENTIRE FILE

"""

from __future__ import annotations

import enum
import os
import sys
from typing import List, Union, Callable, Generator, Any, Dict

import colorama
import pandas as pd
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

import code_analyzer as _code_analyzer
from code_analyzer import constants
from code_analyzer.container_comment import ContainerComment
from code_analyzer.interpretable import Interpretable
from code_analyzer.trace_call_result import TraceCallResult

colorama.init()

BORDER_SPACE_PRIMARY_KEY = "#"
BORDER_SPACE_SECONDARY_KEY = "-"

BORDER_SPACE_PRIMARY_AMOUNT = 100
BORDER_SPACE_SECONDARY_AMOUNT = 50

BORDER_SPACE_PRIMARY = BORDER_SPACE_PRIMARY_KEY * BORDER_SPACE_PRIMARY_AMOUNT
BORDER_SPACE_SECONDARY = BORDER_SPACE_SECONDARY_KEY * BORDER_SPACE_SECONDARY_AMOUNT

STR_CODE_ANALYSIS_HEADER: str = "{}\n{}\n{}\n".format(BORDER_SPACE_PRIMARY,
                                                      "*** CODE ANALYSIS ***",
                                                      BORDER_SPACE_PRIMARY)

STR_EXECUTION_ANALYSIS_HEADER: str = "{}\n{}\n{}\n".format(BORDER_SPACE_SECONDARY,
                                                           "Execution Analysis",
                                                           BORDER_SPACE_SECONDARY)

STR_LINE_OF_CODE_ANALYSIS_HEADER: str = "{}\n{}\n{}\n".format(BORDER_SPACE_SECONDARY,
                                                              "Line of code Analysis",
                                                              BORDER_SPACE_SECONDARY)

RICH_SYNTAX_THEME = "monokai"
RICH_SYNTAX_LEXER = "python"

RICH_TABLE_STYLE = "bold white on black"
RICH_TABLE_HEADER_STYLE = "bold white on black"


##########

class Attribute(enum.Enum):
    EXECUTION_INDEX = enum.auto()  # Index that represents when a line of code has been executed
    LINE_NUMBER = enum.auto()  # Line number
    INDENT_DEPTH_BY_SCOPE = enum.auto()  # (Scope Depth) How deep the scope is
    INDENT_DEPTH = enum.auto()  # How many 4 spaces are needed to place the code in the correct place
    INTERPRETABLE_COUNT = enum.auto()  # The count number for the current line being executed
    CODE_SPACING = enum.auto()  # The literal spacing before the actual code being executed
    CODE = enum.auto()  # Code being executed
    DICT_K_VARIABLE_V_VALUE__FRAME_F_LOCALS = enum.auto()  # The variable's and their values in the current scope
    COMMENT = enum.auto()  # Comments made by the programmer

    ##########
    FILENAME_FULL = enum.auto()
    CALL_COUNT = enum.auto()


class ContainerMapping:

    def __init__(self,
                 name: str,
                 str_format: str,
                 ):
        self.name: str = name
        self.str_format: str = str_format


DICT_K_ATTRIBUTE_V_DATA = Dict[Attribute, Any]

DICT_K_ATTRIBUTE_V_MAPPING_CONTAINER_ATTRIBUTE: Dict[Attribute, ContainerMapping] = {

    # ----- Pre Code -----
    Attribute.EXECUTION_INDEX: ContainerMapping(
        "Execution Index",
        "{:<16}",
    ),
    Attribute.LINE_NUMBER: ContainerMapping(
        "Line #",
        "{:<8}"
    ),
    Attribute.INDENT_DEPTH_BY_SCOPE: ContainerMapping(
        "Scope depth",
        "{:<14}"
    ),
    Attribute.INDENT_DEPTH: ContainerMapping(
        "Indent depth",
        "{:<14}"
    ),
    Attribute.INTERPRETABLE_COUNT: ContainerMapping(
        "Interpretable Count",
        "{:<22}"
    ),
    Attribute.CODE_SPACING: ContainerMapping(
        "",
        "{}"
    ),

    # ----- Code -----
    Attribute.CODE: ContainerMapping(
        "Code",
        "{}"
    ),

    # ----- Post Code (Text right after code) -----
    Attribute.DICT_K_VARIABLE_V_VALUE__FRAME_F_LOCALS: ContainerMapping(
        "{Variable: Value}",
        "  {}"
    ),
    Attribute.COMMENT: ContainerMapping(
        "(Comments)",
        "  {}"
    ),

    ####################

    Attribute.FILENAME_FULL: ContainerMapping(
        "Filename",
        "{}"
    ),
    Attribute.CALL_COUNT: ContainerMapping(
        "Call Count",
        "{}"
    )
}


def get_str_dict_interpretable_data(dict_interpretable_data: DICT_K_ATTRIBUTE_V_DATA) -> str:
    """
    Given a dict, make it into a string

    Notes:
        Assumes that the dict is ordered so python>=3.6 is required

        Given dict_interpretable_data, use DICT_K_ATTRIBUTE_V_MAPPING_CONTAINER_ATTRIBUTE to get the format called F
        using the KEY from dict_interpretable_data, then use F to format the VALUE from dict_interpretable_data

    References:
        Are dictionaries ordered in Python 3.6+?
            Contributors:
    https://github.com/josephedradan

Reference:
                https://stackoverflow.com/questions/39980323/are-dictionaries-ordered-in-python-3-6

        Converting dict to OrderedDict
            Contributors:
    https://github.com/josephedradan

Reference:
                https://stackoverflow.com/questions/15711755/converting-dict-to-ordereddict

        class typing.OrderedDict(collections.OrderedDict, MutableMapping[KT, VT])
            Notes:
                typing.OrderedDict came in at python==3.7.2 so can't type hint OrderedDict when wanting to support
                lower versions of python.

            Joseph Notes:
                dicts before python==3.6 are unordered, OrderedDict is supported in python versions lower than 3.6,
                Type hinting for OrderedDict is supported in 3.7.2. Therefore I will not support python<=3.6

            Contributors:
    https://github.com/josephedradan

Reference:
                https://docs.python.org/3/library/typing.html#typing.OrderedDict


    :param dict_interpretable_data:
    :return:
    """

    list_string: List[str] = []

    for key, value in dict_interpretable_data.items():

        if key == Attribute.DICT_K_VARIABLE_V_VALUE__FRAME_F_LOCALS or key == Attribute.COMMENT:
            if Attribute.CODE in dict_interpretable_data and not value:
                continue

        list_string.append(DICT_K_ATTRIBUTE_V_MAPPING_CONTAINER_ATTRIBUTE[key].str_format.format(value))

    str_ = "".join(
        list_string
    )

    return str_


##########

class DataIntermediateInterpretable:

    def __init__(self, interpretable: Interpretable):
        super().__init__()
        self.interpretable = interpretable

        #####

        self.execution_index_relative: Union[int, None] = self.interpretable.get_execution_index_relative()

        self.trace_call_result: TraceCallResult = self.interpretable.get_trace_call_result_primary()

        self.filename_full: str = self.trace_call_result.filename_full

        self.line_number: int = self.trace_call_result.get_code_line_number()

        self.indent_depth_by_scope: int = self.interpretable.get_scope_parent().get_indent_depth_scope()

        self.indent_depth: int = self.trace_call_result.get_indent_depth_corrected()

        self.interpretable_count = self.interpretable.get_interpretable_count()

        self.code_spacing: str
        self.code: str
        self.code_spacing, self.code = self.trace_call_result.get_spacing_corrected_and_line()

        self.dict_k_variable_v_value__frame_f_locals: dict = (
            self.trace_call_result.get_frame_f_locals_filtered_by_set_variable_exclusion_filtered_by_frame_f_locals_previous()
        )

        self.comment: ContainerComment = self.interpretable.get_container_comment()

        #####

    def get_dict(self) -> DICT_K_ATTRIBUTE_V_DATA:
        """
        Initialize the starting key value pairs in the dict

        :return:
        """
        return {
            Attribute.EXECUTION_INDEX: self.execution_index_relative,
            Attribute.LINE_NUMBER: self.line_number,
            Attribute.INDENT_DEPTH_BY_SCOPE: self.indent_depth_by_scope,
            Attribute.INDENT_DEPTH: self.indent_depth,
            Attribute.INTERPRETABLE_COUNT: self.interpretable_count,
            Attribute.CODE_SPACING: self.code_spacing,
            Attribute.CODE: self.code,
            Attribute.DICT_K_VARIABLE_V_VALUE__FRAME_F_LOCALS: self.dict_k_variable_v_value__frame_f_locals,
            Attribute.COMMENT: self.comment,
            Attribute.FILENAME_FULL: self.filename_full
        }


class Style(enum.Enum):
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


STYLES = Union[Style, None]


class CodeAnalyzerPrinter:

    def __init__(self, code_analyzer: _code_analyzer.CodeAnalyzer):
        self.code_analyzer: _code_analyzer.CodeAnalyzer = code_analyzer

    @staticmethod
    def _get_list_attribute_allowed_execution_analysis() -> List[Attribute]:
        """
        Notes:
            Commenting out a value line will automatically be reflected in the table

        :return:
        """
        list_attribute = [
            Attribute.EXECUTION_INDEX,
            Attribute.LINE_NUMBER,
            Attribute.INDENT_DEPTH_BY_SCOPE,
            Attribute.INDENT_DEPTH,
            Attribute.INTERPRETABLE_COUNT,
            Attribute.CODE_SPACING,
            Attribute.CODE,
            Attribute.DICT_K_VARIABLE_V_VALUE__FRAME_F_LOCALS,
            Attribute.COMMENT,
        ]

        return list_attribute

    @staticmethod
    def _get_list_attribute_allowed_line_of_code_analysis() -> List[Attribute]:
        """
        Notes:
            Commenting out a value line will automatically be reflected in the table

        :return:
        """
        list_attribute = [
            Attribute.EXECUTION_INDEX,
            # Attribute.LINE_NUMBER,
            Attribute.INDENT_DEPTH_BY_SCOPE,
            # Attribute.INDENT_DEPTH,
            Attribute.INTERPRETABLE_COUNT,
            # Attribute.CODE_SPACING,
            # Attribute.CODE,
            Attribute.DICT_K_VARIABLE_V_VALUE__FRAME_F_LOCALS,
            Attribute.COMMENT,
        ]

        return list_attribute

    @staticmethod
    def _get_list_attribute_allowed_line_of_code_analysis_shared() -> List[Attribute]:
        """
        Notes:
            Commenting out a value line will automatically be reflected in the table

        :return:
        """
        list_attribute = [
            Attribute.FILENAME_FULL,
            Attribute.LINE_NUMBER,
            Attribute.CODE,
            Attribute.CALL_COUNT,
        ]

        return list_attribute

    def print(self, print_function: Callable = print, style: STYLES = Style.COLORAMA):
        """
        :param style:
        :param print_function:
        :return:
        """
        header = STR_CODE_ANALYSIS_HEADER

        str_full = "{}\n{}\n\n{}".format(
            header,
            self.get_str_execution_analysis(style),
            self.get_str_line_of_code_analysis(style),
        )

        print_function(str_full)

    def get_str_execution_analysis(self, style: STYLES = None) -> str:

        str_header_main = STR_EXECUTION_ANALYSIS_HEADER

        dict_k_attribute_v_attribute_name = {
            attribute_name: DICT_K_ATTRIBUTE_V_MAPPING_CONTAINER_ATTRIBUTE[attribute_name].name
            for attribute_name in self._get_list_attribute_allowed_execution_analysis()
        }

        str_column_names: str = get_str_dict_interpretable_data(dict_k_attribute_v_attribute_name)

        def get_str_row_interpretable(interpretable: Interpretable) -> str:
            """
            Given an interpretable, make a dict of it's variables that will be used in
            str_execution_analysis. From that dict a string will be made

            :param interpretable:
            :return:
            """
            nonlocal dict_k_attribute_v_attribute_name
            nonlocal style

            dict_k_attribute_v_data = DataIntermediateInterpretable(interpretable).get_dict()

            # Dict with allowed columns based on what exists in dict_k_attribute_v_attribute_name
            dict_k_attribute_v_data_filtered = {
                k: v for k, v in dict_k_attribute_v_data.items() if
                k in dict_k_attribute_v_attribute_name
            }

            dict_k_attribute_v_data_styled = _get_dict_interpretable_data_styled(
                interpretable,
                dict_k_attribute_v_data_filtered,
                style,
            )

            string = get_str_dict_interpretable_data(dict_k_attribute_v_data_styled)

            return string

        generator_str_row_interpretable: Generator[str, None, None] = (
            get_str_row_interpretable(interpretable) for interpretable in self.code_analyzer.list_interpretable
            if interpretable.visibility is True
        )

        str_full = "{}\n{}\n{}".format(
            str_header_main,
            str_column_names,
            "\n".join(generator_str_row_interpretable)
        )

        return str_full

    def get_str_line_of_code_analysis(self, style: STYLES = None) -> str:
        """

        Notes:
            Recall that interpretables in self.code_analyzer.dict_k_interpretable_v_list_interpretable
            are grouped by .get_trace_call_result_primary call's
        :return:
        """
        str_header = STR_LINE_OF_CODE_ANALYSIS_HEADER

        list_str_information_full: List[str] = []

        for interpretable, list_interpretable in self.code_analyzer.dict_k_interpretable_v_list_interpretable.items():
            trace_call_result = interpretable.get_trace_call_result_primary()

            count = len(list_interpretable)

            dict_shared = {}

            for attribute in self._get_list_attribute_allowed_line_of_code_analysis_shared():

                key = DICT_K_ATTRIBUTE_V_MAPPING_CONTAINER_ATTRIBUTE[attribute].name

                value = DataIntermediateInterpretable(interpretable).get_dict().get(attribute)

                # Stuff that can't be found in a DataIntermediateInterpretable's dict
                if attribute == Attribute.CALL_COUNT:
                    value = count

                #####

                # Colorama styling
                if style == Style.COLORAMA:

                    if attribute == Attribute.FILENAME_FULL:
                        key = "{}{}{}".format(colorama.Fore.MAGENTA, key, colorama.Style.RESET_ALL)

                    elif attribute == Attribute.CODE:
                        key = colorama.Fore.GREEN + key + colorama.Style.RESET_ALL
                        value = "{}{}{}".format(colorama.Fore.RED, key, colorama.Style.RESET_ALL)
                    elif attribute == Attribute.LINE_NUMBER:
                        pass

                    elif attribute == Attribute.CALL_COUNT:
                        key = colorama.Fore.BLUE + key + colorama.Style.RESET_ALL

                #####

                dict_shared[key] = value

            str_header_body = "\n".join("{}: {}".format(k, v) for k, v in dict_shared.items())

            list_str_information_full.append(str_header_body)

            def generator(attribute_: Attribute, list_interpretable_: List[Interpretable]):
                """
                Non late binding generator

                Notes:
                    Due to writing a generator comprehension in the loop below causing a late binding issue,
                    this generator prevents that problem

                :param attribute_:
                :param list_interpretable_:
                :return:
                """
                for _inter in list_interpretable_:
                    yield DataIntermediateInterpretable(_inter).get_dict().get(attribute_)

            dict_table_body = {}
            for attribute in self._get_list_attribute_allowed_line_of_code_analysis():
                dict_table_body[DICT_K_ATTRIBUTE_V_MAPPING_CONTAINER_ATTRIBUTE[attribute].name] = generator(
                    attribute,
                    list_interpretable
                )

            df_information = pd.DataFrame.from_dict(dict_table_body)

            # df_information.index.name = "Index"

            # Temporarily set display.max_rows to be unlimited
            with pd.option_context('display.max_rows', None, ):
                list_str_information_full.append(df_information.to_string())

            list_str_information_full.append("\n")

        str_full = "{}\n{}\n".format(
            str_header,
            "\n".join(list_str_information_full),
        )

        return str_full

    def print_rich(self, console: Union[Console, None] = None):

        if console is None:
            # Note: Writing to a file will only have plain text
            console = Console(
                soft_wrap=True,
                # record=True,
            )

        console.print(Text(STR_CODE_ANALYSIS_HEADER, style=RICH_TABLE_STYLE))
        self._do_rich_execution_analysis(console)
        console.print("\n")
        self._do_rich_line_of_code_analysis(console)

    def _do_rich_execution_analysis(self, console: Console):
        """
        Do the rich version of execution analysis

        Notes:
            On the subject of rich styles,

        :param console:
        :return:
        """
        console.print(Text(STR_EXECUTION_ANALYSIS_HEADER, style=RICH_TABLE_STYLE))

        dict_k_attribute_v_attribute_name = {
            attribute_name: DICT_K_ATTRIBUTE_V_MAPPING_CONTAINER_ATTRIBUTE[attribute_name].name
            for attribute_name in self._get_list_attribute_allowed_execution_analysis()
        }

        _bool_code_exists = dict_k_attribute_v_attribute_name.get(Attribute.CODE, None) is not None

        table = Table(
            # title=STR_EXECUTION_ANALYSIS_HEADER,
            expand=True,
            width=(
                    self.code_analyzer.length_line_most_chars_with_comments_with_dict_k_variable_v_value +
                    len("".join(dict_k_attribute_v_attribute_name.values()))
            ),
            style=RICH_TABLE_STYLE
        )

        if _bool_code_exists:

            _str_dict_k_variable_v_attribute = ""
            if DICT_K_ATTRIBUTE_V_MAPPING_CONTAINER_ATTRIBUTE.get(Attribute.DICT_K_VARIABLE_V_VALUE__FRAME_F_LOCALS,
                                                                  None) is not None:
                _str_dict_k_variable_v_attribute = DICT_K_ATTRIBUTE_V_MAPPING_CONTAINER_ATTRIBUTE[
                    Attribute.DICT_K_VARIABLE_V_VALUE__FRAME_F_LOCALS].str_format.format(
                    DICT_K_ATTRIBUTE_V_MAPPING_CONTAINER_ATTRIBUTE[
                        Attribute.DICT_K_VARIABLE_V_VALUE__FRAME_F_LOCALS].name
                ).rstrip()

            _str_list_comment = ""
            if DICT_K_ATTRIBUTE_V_MAPPING_CONTAINER_ATTRIBUTE.get(Attribute.COMMENT, None) is not None:
                _str_list_comment = DICT_K_ATTRIBUTE_V_MAPPING_CONTAINER_ATTRIBUTE[
                    Attribute.COMMENT].str_format.format(
                    DICT_K_ATTRIBUTE_V_MAPPING_CONTAINER_ATTRIBUTE[Attribute.COMMENT].name
                ).rstrip()

            dict_k_attribute_v_attribute_name[Attribute.CODE] = "{}{}{}".format(
                DICT_K_ATTRIBUTE_V_MAPPING_CONTAINER_ATTRIBUTE[Attribute.CODE].name,
                _str_dict_k_variable_v_attribute,
                _str_list_comment
            )

        for attribute, attribute_name in dict_k_attribute_v_attribute_name.items():

            if _bool_code_exists and (
                    attribute == Attribute.CODE_SPACING or
                    attribute == Attribute.DICT_K_VARIABLE_V_VALUE__FRAME_F_LOCALS or
                    attribute == Attribute.COMMENT):
                pass
            elif attribute == Attribute.CODE_SPACING:
                # Never have a column for code spacing because it's empty
                pass
            elif attribute == Attribute.CODE:
                table.add_column(
                    dict_k_attribute_v_attribute_name[attribute],
                    no_wrap=True,
                    width=self.code_analyzer.length_line_most_chars_with_comments_with_dict_k_variable_v_value,
                    header_style=RICH_TABLE_HEADER_STYLE,
                    style=RICH_TABLE_STYLE
                )
            else:
                table.add_column(
                    dict_k_attribute_v_attribute_name[attribute],
                    no_wrap=True,
                    header_style=RICH_TABLE_HEADER_STYLE,
                    style=RICH_TABLE_STYLE
                )

            # Doesn't work as intended
            # if i == 5:
            #     table.add_column(
            #         attribute_name,
            #         no_wrap=True,
            #         style=Syntax.get_theme("python").get_style_for_token()
            #     )
            # else:
            #     table.add_column(
            #         attribute_name,
            #         no_wrap=True,
            #     )

        for interpretable in self.code_analyzer.list_interpretable:

            if interpretable.visibility is False:
                continue

            trace_call_result = interpretable.get_trace_call_result_primary()

            dict_k_attribute_v_data = DataIntermediateInterpretable(interpretable).get_dict()

            dict_k_attribute_v_data__filtered = {k: v for k, v in dict_k_attribute_v_data.items() if
                                                 k in dict_k_attribute_v_attribute_name}

            """
            Notes:
                Rich styling:
                    Styles for "style" can be found at https://rich.readthedocs.io/en/stable/style.html 
                    Colors for "style" can be found at https://rich.readthedocs.io/en/stable/appendix/colors.html
            """
            if dict_k_attribute_v_data__filtered.get(Attribute.DICT_K_VARIABLE_V_VALUE__FRAME_F_LOCALS,
                                                     None) is not None:
                # Removes empty dict string
                dict_k_attribute_v_data__filtered[Attribute.DICT_K_VARIABLE_V_VALUE__FRAME_F_LOCALS] = (
                    dict_k_attribute_v_data__filtered[Attribute.DICT_K_VARIABLE_V_VALUE__FRAME_F_LOCALS] if
                    dict_k_attribute_v_data__filtered[Attribute.DICT_K_VARIABLE_V_VALUE__FRAME_F_LOCALS] else ""
                )

                _str_dict_k_variable_v_value = (
                    DICT_K_ATTRIBUTE_V_MAPPING_CONTAINER_ATTRIBUTE[
                        Attribute.DICT_K_VARIABLE_V_VALUE__FRAME_F_LOCALS].str_format.format(
                        dict_k_attribute_v_data__filtered[Attribute.DICT_K_VARIABLE_V_VALUE__FRAME_F_LOCALS]
                    )
                ).rstrip()

                # The commented out code below does not make a difference because text object style carries over
                # text_dict_k_variable_v_value: Text = Syntax(
                #     "",
                #     lexer=RICH_SYNTAX_LEXER,
                #     theme=RICH_SYNTAX_THEME).highlight(_str_dict_k_variable_v_value)
                #
                # text_dict_k_variable_v_value.stylize('dark_orange')
                #
                # text_dict_k_variable_v_value.rstrip()
                #
                # dict_k_attribute_v_data__filtered[Attribute.DICT_K_VARIABLE_V_VALUE__FRAME_F_LOCALS] =(
                #     text_dict_k_variable_v_value
                # )

                dict_k_attribute_v_data__filtered[Attribute.DICT_K_VARIABLE_V_VALUE__FRAME_F_LOCALS] = Text(
                    _str_dict_k_variable_v_value,
                    # style="rgb(255,0,0)",  # Red
                    style="dark_orange",  # rgb(215,95,0)
                )

            if dict_k_attribute_v_data__filtered.get(Attribute.COMMENT, None) is not None:
                # Removes empty list string
                dict_k_attribute_v_data__filtered[Attribute.COMMENT] = (
                    dict_k_attribute_v_data__filtered[Attribute.COMMENT] if
                    dict_k_attribute_v_data__filtered[Attribute.COMMENT] else ""
                )

                _str_comment = (DICT_K_ATTRIBUTE_V_MAPPING_CONTAINER_ATTRIBUTE[Attribute.COMMENT].str_format.format(
                    dict_k_attribute_v_data__filtered[Attribute.COMMENT]
                )).rstrip()

                dict_k_attribute_v_data__filtered[Attribute.COMMENT] = Text(
                    _str_comment,
                    style="rgb(255,0,0)",  # Red
                    # style="dark_orange",  # rgb(215,95,0)
                )

            if (dict_k_attribute_v_data__filtered.get(Attribute.CODE_SPACING, None) is not None and
                    dict_k_attribute_v_data__filtered.get(Attribute.CODE, None) is not None and
                    _bool_code_exists):
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

                text_code_spacing: Text = Syntax("", lexer=RICH_SYNTAX_LEXER, theme=RICH_SYNTAX_THEME).highlight(
                    dict_k_attribute_v_data__filtered[Attribute.CODE_SPACING]
                )

                # *** DUMB WAY TO REMOVE THE NEWLINE AT THE END AND NOT THE SPACES ***
                text_code_spacing = text_code_spacing.split()[0]

                dict_k_attribute_v_data__filtered.pop(Attribute.CODE_SPACING)

                text_code: Text = Syntax("", lexer=RICH_SYNTAX_LEXER, theme=RICH_SYNTAX_THEME).highlight(
                    dict_k_attribute_v_data__filtered[Attribute.CODE]
                )

                text_code.rstrip()  # Removes newline that was added for some reason...

                # ----- Styling ----- #

                # Function definition
                if (trace_call_result.get_python_keyword() == constants.Keyword.DEF and
                        trace_call_result.get_event() == constants.Event.LINE):
                    text_code.stylize("on rgb(0,0,135)")  # dark_blue

                # Function call
                elif (trace_call_result.get_python_keyword() == constants.Keyword.DEF and
                      trace_call_result.get_event() == constants.Event.CALL):
                    text_code.stylize("on rgb(0,95,0)")  # dark_green

                # Class definition
                elif (trace_call_result.get_python_keyword() == constants.Keyword.CLASS and
                      trace_call_result.get_event() == constants.Event.LINE):
                    # text_code.stylize("on rgb(175,0,215)")  # dark_violet
                    text_code.stylize("on rgb(0,0,135)")  # dark_blue

                # Fallback color for all Event.CALL
                elif trace_call_result.get_event() == constants.Event.CALL:
                    text_code.stylize("on rgb(0,95,0)")  # dark_green

                ##########

                text_code_spacing.append_text(text_code)

                if dict_k_attribute_v_data__filtered.get(Attribute.DICT_K_VARIABLE_V_VALUE__FRAME_F_LOCALS,
                                                         None) is not None:
                    text_code_spacing.append_text(
                        dict_k_attribute_v_data__filtered[Attribute.DICT_K_VARIABLE_V_VALUE__FRAME_F_LOCALS])

                    dict_k_attribute_v_data__filtered.pop(Attribute.DICT_K_VARIABLE_V_VALUE__FRAME_F_LOCALS)

                if dict_k_attribute_v_data__filtered.get(Attribute.COMMENT, None) is not None:
                    text_code_spacing.append_text(dict_k_attribute_v_data__filtered[Attribute.COMMENT])

                    dict_k_attribute_v_data__filtered.pop(Attribute.COMMENT)

                dict_k_attribute_v_data__filtered[Attribute.CODE] = text_code_spacing

                # print(f"{text_code_spacing.markup=}")  # DEBUGGING: Check what the markup is

            list_data: List[str] = [(str(data) if isinstance(data, int) else data)
                                    for data in dict_k_attribute_v_data__filtered.values()]

            table.add_row(*list_data)

            # DEBUGGING: If the width of the table is too big, then it will reset the console's width to 79
            # print(f"{self.console.size=}")

        console.print(table)

    def _do_rich_line_of_code_analysis(self, console: Console):
        """
        Do the rich version of line of code analysis

        :param console:
        :return:
        """
        console.print(Text(STR_LINE_OF_CODE_ANALYSIS_HEADER, style=RICH_TABLE_STYLE))

        # WARNING: Suboptimal since this calculation was made before
        __width_additional = len("".join({
                                             attribute_name: DICT_K_ATTRIBUTE_V_MAPPING_CONTAINER_ATTRIBUTE[
                                                 attribute_name].name
                                             for attribute_name in self._get_list_attribute_allowed_execution_analysis()
                                         }.values()))

        for interpretable, list_interpretable in self.code_analyzer.dict_k_interpretable_v_list_interpretable.items():
            table_shared = Table(
                expand=True,
                style=RICH_TABLE_STYLE,
                width=(
                        self.code_analyzer.length_line_most_chars_with_comments_with_dict_k_variable_v_value +
                        __width_additional
                ),
            )

            table_shared.add_column(
                "Name",
                header_style=RICH_TABLE_HEADER_STYLE,
                style=RICH_TABLE_STYLE
            )

            table_shared.add_column(
                "Value",
                header_style=RICH_TABLE_HEADER_STYLE,
                style=RICH_TABLE_STYLE
            )

            ########################

            trace_call_result = interpretable.get_trace_call_result_primary()

            count = len(list_interpretable)

            for attribute in self._get_list_attribute_allowed_line_of_code_analysis_shared():

                text_key: Text = Text(str(DICT_K_ATTRIBUTE_V_MAPPING_CONTAINER_ATTRIBUTE[attribute].name))

                text_value: Text = Text(str(DataIntermediateInterpretable(interpretable).get_dict().get(attribute)))

                # Stuff that can't be found in a DataIntermediateInterpretable's dict
                if attribute == Attribute.CALL_COUNT:
                    text_value = Text(str(count))

                # ----- Styling ----- #

                # Filename
                if attribute == Attribute.FILENAME_FULL:
                    text_key.stylize("bright_magenta")  # rgb(175,0,255)

                # Line
                elif attribute == Attribute.LINE_NUMBER:
                    pass

                # Code
                elif attribute == Attribute.CODE:
                    text_key.stylize("bright_green")
                    text_value = Syntax("", lexer=RICH_SYNTAX_LEXER, theme=RICH_SYNTAX_THEME).highlight(
                        str(text_value)
                    )
                    text_value.rstrip()  # Removes newline that was added for some reason...

                # Call Count
                elif attribute == Attribute.CALL_COUNT:
                    text_key.stylize("bright_cyan")

                ##########

                table_shared.add_row(text_key, text_value)

            console.print(table_shared)

            ########################

            table_body = Table(
                expand=True,
                style=RICH_TABLE_STYLE,
                width=(
                        self.code_analyzer.length_line_most_chars_with_comments_with_dict_k_variable_v_value +
                        __width_additional
                ),
            )

            for attribute in self._get_list_attribute_allowed_line_of_code_analysis():
                table_body.add_column(
                    DICT_K_ATTRIBUTE_V_MAPPING_CONTAINER_ATTRIBUTE[attribute].name,
                    header_style=RICH_TABLE_HEADER_STYLE,
                    style=RICH_TABLE_STYLE,
                )

            for interpretable_inner in list_interpretable:
                data_intermediate_interpretable = DataIntermediateInterpretable(interpretable_inner)

                dict_data_intermediate_interpretable = data_intermediate_interpretable.get_dict()

                list_data = [str(dict_data_intermediate_interpretable.get(attribute)) for attribute in
                             self._get_list_attribute_allowed_line_of_code_analysis()]

                table_body.add_row(*list_data)

            console.print(table_body)
            console.print("\n")

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

    def export_to_txt(self):
        """
        Write the non rich version of the code analysis to a file

        :return:
        """
        # print(os.path.basename(__file__))
        # print(sys.argv[0])
        # print(os.path.basename(sys.argv[0]))

        basename = os.path.basename(sys.argv[0])
        basename_no_ext = os.path.splitext(basename)[0]

        output_name = f"{basename_no_ext}_code_analysis.txt"

        with open(output_name, "w") as file:
            self.print(print_function=file.write, style=None)

    def export_rich_to_html(self):
        """
        Will write the terminal first then export the console's results to a html

        :return:
        """

        # Note: Writing to a file will only have plain text
        console = Console(
            soft_wrap=True,
            record=True,
        )

        self.print_rich(console)

        basename = os.path.basename(sys.argv[0])
        basename_no_ext = os.path.splitext(basename)[0]

        output_name = f"{basename_no_ext}_code_analysis_rich.html"

        console.save_html(output_name)  # By default clear=True to clear the buffer


def _get_dict_interpretable_data_styled(interpretable: Interpretable,
                                        dict_interpretable_data: DICT_K_ATTRIBUTE_V_DATA,
                                        style: STYLES = None) -> DICT_K_ATTRIBUTE_V_DATA:
    """
    Style dict_interpretable_data

    Notes:
        This code does not care if keys exist or not

    :return:
    """

    dict_temp = dict_interpretable_data

    dict_temp[Attribute.DICT_K_VARIABLE_V_VALUE__FRAME_F_LOCALS] = (
        dict_temp[Attribute.DICT_K_VARIABLE_V_VALUE__FRAME_F_LOCALS] if dict_temp[
            Attribute.DICT_K_VARIABLE_V_VALUE__FRAME_F_LOCALS] else ""
    )

    dict_temp[Attribute.COMMENT] = (
        dict_temp[Attribute.COMMENT] if dict_temp[Attribute.COMMENT] else ""
    )

    # TODO: Redesign entire file
    if style == Style.COLORAMA:

        if dict_temp[Attribute.DICT_K_VARIABLE_V_VALUE__FRAME_F_LOCALS]:
            dict_temp[Attribute.DICT_K_VARIABLE_V_VALUE__FRAME_F_LOCALS] = (
                    colorama.Fore.RED + str(
                dict_temp[Attribute.DICT_K_VARIABLE_V_VALUE__FRAME_F_LOCALS]) + colorama.Style.RESET_ALL
            )

        if dict_temp[Attribute.COMMENT]:
            dict_temp[Attribute.COMMENT] = (
                    colorama.Fore.MAGENTA + str(dict_temp[Attribute.COMMENT]) + colorama.Style.RESET_ALL
            )

        # TODO: Design the below better
        trace_call_result = interpretable.get_trace_call_result_primary()

        dict_temp[Attribute.CODE] = _get_str_code_styled(trace_call_result, style)

    return dict_temp


def _get_str_code_styled(trace_call_result: TraceCallResult, style: STYLES = None) -> str:
    """
    Given a TraceCallResult, return a colored version of its __str__()

    :return:
    """
    spacing, line = trace_call_result.get_spacing_corrected_and_line()

    if style == Style.COLORAMA and line:

        color_fore: Union[str, colorama.ansi.AnsiFore] = ""
        color_back: Union[str, colorama.ansi.AnsiBack] = ""

        # Function definition
        if (trace_call_result.get_python_keyword() == constants.Keyword.DEF and
                trace_call_result.get_event() == constants.Event.LINE):
            color_fore = colorama.Fore.BLUE

        # Function call
        elif (trace_call_result.get_python_keyword() == constants.Keyword.DEF and
              trace_call_result.get_event() == constants.Event.CALL):
            color_fore = colorama.Fore.GREEN

        # Class definition
        elif (trace_call_result.get_python_keyword() == constants.Keyword.CLASS and
              trace_call_result.get_event() == constants.Event.LINE):
            # color_fore = colorama.Fore.CYAN
            color_fore = colorama.Fore.BLUE

        # Fallback color for all Event.CALL
        elif trace_call_result.get_event() == constants.Event.CALL:
            color_fore = colorama.Fore.GREEN

        return "{}{}{}{}".format(color_fore, color_back, line, colorama.Style.RESET_ALL)

    return line
