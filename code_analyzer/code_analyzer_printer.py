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

import enum
import os
import sys
from typing import List, Union, Callable, Literal, Generator, Any, Dict

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
    EXECUTION_INDEX = enum.auto()
    LINE_NUMBER = enum.auto()
    INDENT_DEPTH_BY_SCOPE = enum.auto()
    INDENT_DEPTH = enum.auto()
    EXECUTION_COUNT = enum.auto()
    CODE_SPACING = enum.auto()
    CODE = enum.auto()
    DICT_K_VARIABLE_V_VALUE = enum.auto()
    LIST_STR_COMMENT = enum.auto()

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
        "{:<10}"
    ),
    Attribute.INDENT_DEPTH_BY_SCOPE: ContainerMapping(
        "Scope depth",
        "{:<14}"
    ),
    Attribute.INDENT_DEPTH: ContainerMapping(
        "Indent depth",
        "{:<14}"
    ),
    Attribute.EXECUTION_COUNT: ContainerMapping(
        "Execution Count",
        "{:<18}"
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

    # ----- Post Code -----
    Attribute.DICT_K_VARIABLE_V_VALUE: ContainerMapping(
        "{Variable: Value}",
        " {}"
    ),
    Attribute.LIST_STR_COMMENT: ContainerMapping(
        "[Comment]",
        " {}"
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
    Notes:
        Assumes that the dict is ordered so python>=3.6 is required

        Given dict_interpretable_data, use DICT_K_ATTRIBUTE_V_MAPPING_CONTAINER_ATTRIBUTE to get the format called F
        using the KEY from dict_interpretable_data, then use F to format the VALUE from dict_interpretable_data

    References:
        Are dictionaries ordered in Python 3.6+?
            Reference:
                https://stackoverflow.com/questions/39980323/are-dictionaries-ordered-in-python-3-6

        Converting dict to OrderedDict
            Reference:
                https://stackoverflow.com/questions/15711755/converting-dict-to-ordereddict

        class typing.OrderedDict(collections.OrderedDict, MutableMapping[KT, VT])
            Notes:
                typing.OrderedDict came in at python==3.7.2 so can't type hint OrderedDict when wanting to support
                lower versions of python.

            Joseph Notes:
                dicts before python==3.6 are unordered, OrderedDict is supported in python versions lower than 3.6,
                Type hinting for OrderedDict is supported in 3.7.2. Therefore I will not support python<=3.6

            Reference:
                https://docs.python.org/3/library/typing.html#typing.OrderedDict


    :param dict_interpretable_data:
    :return:
    """

    str_ = "".join([
        DICT_K_ATTRIBUTE_V_MAPPING_CONTAINER_ATTRIBUTE[key].str_format.format(value) for key, value in
        dict_interpretable_data.items()
    ])

    return str_


##########

class DataIntermediateInterpretable:

    def __init__(self, interpretable: Interpretable):
        super().__init__()
        self.interpretable = interpretable

        #####

        self.execution_index_relative: int = self.interpretable.get_execution_index_relative()

        self.trace_call_result: TraceCallResult = self.interpretable.get_trace_call_result_primary()

        self.filename_full: str = self.trace_call_result.filename_full

        self.line_number: int = self.trace_call_result.get_code_line_number()

        self.indent_depth_by_scope: int = self.interpretable.get_scope_parent().get_indent_depth_scope()

        self.indent_depth: int = self.trace_call_result.get_indent_depth_corrected()

        self.execution_count = self.interpretable.get_execution_count()

        self.code_spacing: int
        self.code: int
        self.code_spacing, self.code = self.trace_call_result.get_spacing_corrected_and_line()

        self.dict_k_variable_v_value: dict = interpretable.get_dict_k_variable_v_value()

        self.list_str_comment = self.interpretable.get_list_str_comment()

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
            Attribute.EXECUTION_COUNT: self.execution_count,
            Attribute.CODE_SPACING: self.code_spacing,
            Attribute.CODE: self.code,
            Attribute.DICT_K_VARIABLE_V_VALUE: self.dict_k_variable_v_value,
            Attribute.LIST_STR_COMMENT: self.list_str_comment,
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


STYLES = Literal[Style.COLORAMA, Style.RICH, None]


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
            Attribute.EXECUTION_COUNT,
            Attribute.CODE_SPACING,
            Attribute.CODE,
            Attribute.DICT_K_VARIABLE_V_VALUE,
            Attribute.LIST_STR_COMMENT,
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
            Attribute.EXECUTION_COUNT,
            # Attribute.CODE_SPACING,
            # Attribute.CODE,
            Attribute.DICT_K_VARIABLE_V_VALUE,
            Attribute.LIST_STR_COMMENT,
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

        generator_str_row_interpretable: Generator[str] = (
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

            # WARNING: dict_k_variable_v_value VARIES PER INTERPRETABLE, DON'T USE THIS
            dict_k_variable_v_value = interpretable.get_dict_k_variable_v_value()

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
                        key = colorama.Fore.MAGENTA + key + colorama.Style.RESET_ALL

                    elif attribute == Attribute.CODE:
                        key = colorama.Fore.GREEN + key + colorama.Style.RESET_ALL
                        value = colorama.Fore.RED + value + colorama.Style.RESET_ALL
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
                    self.code_analyzer.length_line_most_chars_with_comments +
                    len("".join(dict_k_attribute_v_attribute_name.values()))
            ),
            style=RICH_TABLE_STYLE
        )

        if _bool_code_exists:

            _str_dict = ""
            if DICT_K_ATTRIBUTE_V_MAPPING_CONTAINER_ATTRIBUTE.get(Attribute.DICT_K_VARIABLE_V_VALUE, None) is not None:
                _str_dict = DICT_K_ATTRIBUTE_V_MAPPING_CONTAINER_ATTRIBUTE[
                    Attribute.DICT_K_VARIABLE_V_VALUE].str_format.format(
                    DICT_K_ATTRIBUTE_V_MAPPING_CONTAINER_ATTRIBUTE[Attribute.DICT_K_VARIABLE_V_VALUE].name
                )

            _str_list = ""
            if DICT_K_ATTRIBUTE_V_MAPPING_CONTAINER_ATTRIBUTE.get(Attribute.LIST_STR_COMMENT, None) is not None:
                _str_list = DICT_K_ATTRIBUTE_V_MAPPING_CONTAINER_ATTRIBUTE[
                    Attribute.LIST_STR_COMMENT].str_format.format(
                    DICT_K_ATTRIBUTE_V_MAPPING_CONTAINER_ATTRIBUTE[Attribute.LIST_STR_COMMENT].name
                )

            dict_k_attribute_v_attribute_name[Attribute.CODE] = "{}{}{}".format(
                DICT_K_ATTRIBUTE_V_MAPPING_CONTAINER_ATTRIBUTE[Attribute.CODE].name,
                _str_dict,
                _str_list
            )

        for attribute, attribute_name in dict_k_attribute_v_attribute_name.items():

            if _bool_code_exists and (
                    attribute == Attribute.CODE_SPACING or
                    attribute == Attribute.DICT_K_VARIABLE_V_VALUE or
                    attribute == Attribute.LIST_STR_COMMENT):
                pass
            elif attribute == Attribute.CODE_SPACING:
                # Never have a column for code spacing because it's empty
                pass
            elif attribute == Attribute.CODE:
                table.add_column(
                    dict_k_attribute_v_attribute_name[attribute],
                    no_wrap=True,
                    width=self.code_analyzer.length_line_most_chars_with_comments,
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
            if dict_k_attribute_v_data__filtered.get(Attribute.DICT_K_VARIABLE_V_VALUE, None) is not None:
                # Removes empty dict string
                dict_k_attribute_v_data__filtered[Attribute.DICT_K_VARIABLE_V_VALUE] = (
                    dict_k_attribute_v_data__filtered[Attribute.DICT_K_VARIABLE_V_VALUE] if
                    dict_k_attribute_v_data__filtered[Attribute.DICT_K_VARIABLE_V_VALUE] else ""
                )

                dict_k_attribute_v_data__filtered[Attribute.DICT_K_VARIABLE_V_VALUE]: Text = Text(
                    DICT_K_ATTRIBUTE_V_MAPPING_CONTAINER_ATTRIBUTE[Attribute.DICT_K_VARIABLE_V_VALUE].str_format.format(
                        dict_k_attribute_v_data__filtered[Attribute.DICT_K_VARIABLE_V_VALUE]),
                    style="rgb(255,0,0)",  # Red
                    # style="dark_orange",
                )

            if dict_k_attribute_v_data__filtered.get(Attribute.LIST_STR_COMMENT, None) is not None:
                # Removes empty list string
                dict_k_attribute_v_data__filtered[Attribute.LIST_STR_COMMENT] = (
                    dict_k_attribute_v_data__filtered[Attribute.LIST_STR_COMMENT] if
                    dict_k_attribute_v_data__filtered[Attribute.LIST_STR_COMMENT] else ""
                )

                dict_k_attribute_v_data__filtered[Attribute.LIST_STR_COMMENT]: Text = Text(
                    DICT_K_ATTRIBUTE_V_MAPPING_CONTAINER_ATTRIBUTE[Attribute.LIST_STR_COMMENT].str_format.format(
                        dict_k_attribute_v_data__filtered[Attribute.LIST_STR_COMMENT]),
                    # style="rgb(255,0,0)",  # Red
                    style="dark_orange",
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

                if dict_k_attribute_v_data__filtered.get(Attribute.DICT_K_VARIABLE_V_VALUE, None) is not None:
                    text_code_spacing.append_text(dict_k_attribute_v_data__filtered[Attribute.DICT_K_VARIABLE_V_VALUE])

                    dict_k_attribute_v_data__filtered.pop(Attribute.DICT_K_VARIABLE_V_VALUE)

                if dict_k_attribute_v_data__filtered.get(Attribute.LIST_STR_COMMENT, None) is not None:
                    text_code_spacing.append_text(dict_k_attribute_v_data__filtered[Attribute.LIST_STR_COMMENT])

                    dict_k_attribute_v_data__filtered.pop(Attribute.LIST_STR_COMMENT)

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
            attribute_name: DICT_K_ATTRIBUTE_V_MAPPING_CONTAINER_ATTRIBUTE[attribute_name].name
            for attribute_name in self._get_list_attribute_allowed_execution_analysis()
        }.values()))

        for interpretable, list_interpretable in self.code_analyzer.dict_k_interpretable_v_list_interpretable.items():
            table_shared = Table(
                expand=True,
                style=RICH_TABLE_STYLE,
                width=(
                        self.code_analyzer.length_line_most_chars_with_comments +
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
                        self.code_analyzer.length_line_most_chars_with_comments +
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

    dict_temp[Attribute.DICT_K_VARIABLE_V_VALUE] = (
        dict_temp[Attribute.DICT_K_VARIABLE_V_VALUE] if dict_temp[
            Attribute.DICT_K_VARIABLE_V_VALUE] else ""
    )

    dict_temp[Attribute.LIST_STR_COMMENT] = (
        dict_temp[Attribute.LIST_STR_COMMENT] if dict_temp[Attribute.LIST_STR_COMMENT] else ""
    )

    if style == Style.COLORAMA:
        dict_temp[Attribute.DICT_K_VARIABLE_V_VALUE] = (
                colorama.Fore.RED + str(dict_temp[Attribute.DICT_K_VARIABLE_V_VALUE]) + colorama.Style.RESET_ALL
        )

        dict_temp[Attribute.LIST_STR_COMMENT] = (
                colorama.Fore.RED + str(dict_temp[Attribute.LIST_STR_COMMENT]) + colorama.Style.RESET_ALL
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

    if style == Style.COLORAMA:

        color_fore: Union[str, colorama.Fore] = ""
        color_back: Union[str, colorama.Back] = ""

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

        return color_fore + color_back + line + colorama.Style.RESET_ALL

    return line
