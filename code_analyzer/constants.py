"""
Created by Joseph Edradan
Github: https://github.com/josephedradan

Date created: 6/23/2022

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

from enum import Enum


class EnumSimple(Enum):

    # def __eq__(self, other):
    #     """
    #     Changing the default behavior because
    #     """
    #     return other == self.value

    @staticmethod
    def get_enum(value) -> EnumSimple:
        """
        Here for convenience because you might not know...
        """
        return EnumSimple(value)


class InterpretableType(EnumSimple):
    pass


class Keyword(InterpretableType):
    AND = "and"
    AS = "as"
    ASSERT = "assert"
    BREAK = "break"
    CASE = "case"
    CLASS = "class"
    CONTINUE = "continue"
    DEF = "def"
    DEL = "del"
    ELIF = "elif"
    ELSE = "else"
    EXCEPT = "except"
    FALSE = "False"
    FINALLY = "finally"
    FOR = "for"
    FROM = "from"
    GLOBAL = "global"
    IF = "if"
    IMPORT = "import"
    IN = "in"
    IS = "is"
    LAMBDA = "lambda"
    MATCH = "match"
    NONE = "None"
    NONLOCAL = "nonlocal"
    NOT = "not"
    OR = "or"
    PASS = "pass"
    RAISE = "raise"
    RETURN = "return"
    TRUE = "True"
    TRY = "try"
    WHILE = "while"
    WITH = "with"
    YIELD = "yield"


class Event(InterpretableType):
    """
    Notes:
        Add more events when the Python version updates

    Reference:
        sys.settrace(tracefunc)
            Notes:
                "Trace functions should have three arguments: frame, str_event, and arg. frame is the current stack frame.
                str_event is a string: 'call', 'line', 'return', 'exception' or 'opcode'. arg depends on the str_event type."
            Reference:
                https://docs.python.org/3/library/sys.html#sys.settrace
    """
    RETURN = 'return'  # tracefunc str_event
    CALL = 'call'  # tracefunc str_event
    LINE = 'line'  # tracefunc str_event
    EXCEPTION = 'exception'  # tracefunc str_event
    OPCODE = 'opcode'  # tracefunc str_event
