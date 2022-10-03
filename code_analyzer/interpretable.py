"""
Created by Joseph Edradan
Github: https://github.com/josephedradan

Date created: 7/3/2022

Purpose:

Details:

Description:

Notes:

IMPORTANT NOTES:

Explanation:

Tags:

Reference:

"""
from typing import Dict, Any, List, Union

from code_analyzer import constants
from code_analyzer import scope
from code_analyzer import trace_call_result as _trace_call_result


class NoTraceCallResult(Exception):
    pass


class Interpretable:

    def __init__(self,
                 scope_parent: scope.Scope,
                 interpretable_type: Union[constants.InterpretableType, None] = None):
        """

        :param scope_parent:
        :param interpretable_type:
        """
        # Parent scope
        self.scope_parent: scope.Scope = scope_parent

        # Immediately add self to scope_parent
        self.scope_parent.add_interpretable(self)

        # The interpretable type of this object
        self.interpretable_type: Union[constants.InterpretableType, None] = interpretable_type

        ##################################################
        """
        Varying Internal variables
        """

        # All TraceCallResult objects related to this interpretable
        self.list_trace_call_result: List[_trace_call_result.TraceCallResult] = []

        # Recorded "Variable: Value" pairs
        self.dict_k_variable_v_value: Dict[str, Any] = {}

        ##################################################
        """
        Analysis variables
        """

        """
        Since an Interpretable object represents a line of code and line of code can be ran multiple times,
        this number represents the execution relative to the other interpretables with teh same line of code
        and file
        """
        self.execution_number_relative: Union[int, None] = None

        """
        Global execution index. This number represents the execution index of this Interpretable i.e, when
        this Interpretable was ran relative to the previously ran interpretables
        """
        self.execution_index_global: Union[int, None] = None

    def set_anlaysis_info(self, execution_number_relative: int, execution_index_global: int):
        """

        :param execution_number_relative:
        :param execution_index_global:
        :return:
        """
        self.execution_number_relative = execution_number_relative
        self.execution_index_global = execution_index_global

    def set_interpretable_type(self, interpretable_type: constants.InterpretableType):
        self.interpretable_type = interpretable_type

    def get_execution_count(self) -> Union[int, None]:
        return self.execution_number_relative

    def get_execution_index_relative(self) -> Union[int, None]:
        return self.execution_index_global

    def get_list_trace_call(self) -> List[_trace_call_result.TraceCallResult]:
        return self.list_trace_call_result

    def add_trace_call_result(self, trace_call_result: _trace_call_result.TraceCallResult):
        """
        Notes:
            This function should not be called from code_analyzer, but from the Scope object
        :param trace_call_result:
        :return:
        """

        # Create a dependency on each other (Necessary for correcting the indent level)
        trace_call_result.assign_interpretable(self)

        self.list_trace_call_result.append(trace_call_result)

    def update_dict_k_variable_v_value_through_exhaustable(self, list_dict_k_variable_v_value: List[Dict[str, Any]]):
        """
        Loop add dict_k_variable_v_value from a list to self.dict_k_variable_v_value


        :param list_dict_k_variable_v_value:
        :return:
        """
        while list_dict_k_variable_v_value:
            self.update_dict_k_variable_v_value(list_dict_k_variable_v_value.pop())

    def update_dict_k_variable_v_value(self, dict_k_variable_v_value: Dict[str, Any]):
        self.dict_k_variable_v_value.update(dict_k_variable_v_value)

    def get_dict_k_variable_v_value(self) -> Dict[str, Any]:
        return self.dict_k_variable_v_value

    def get_trace_call_result_primary(self) -> _trace_call_result.TraceCallResult:
        """
        Get the primary TraceCallResult object that would represent this object
        as its primary TraceCallResult object assuming that hter

        TODO: Redesign, give who decides what is the primary TraceCallResult to the python code analyzer


        :return:
        """
        if not self.list_trace_call_result:
            raise Exception(f"No {_trace_call_result.TraceCallResult.__name__} objects in interpretable")

        trace_call_result_first = self.list_trace_call_result[0]

        trace_call_result_last = self.list_trace_call_result[-1]

        python_key_word = trace_call_result_first.get_python_key_word()

        if self.interpretable_type == constants.Event.RETURN:
            """
            Recall that last TraceCallResult has has the event Event.RETURN
            
            In self._list_trace_call_result_raw by index: 
                0. TraceCallResult with Event == Line Relative to the inner scope_parent
                1. TraceCallResult with Event == Return Relative to the inner scope_parent
            """

            return self.list_trace_call_result[-1]

        elif self.interpretable_type == constants.Keyword.CLASS:
            """
            Recall that this is the definition of the class not the call of it.
            Note that the 0th index TraceCallResult is relative to the outer scope_parent 
            
            In self._list_trace_call_result_raw by index: 
                0. TraceCallResult with Event == Line Relative to the outer scope_parent 
                1. TraceCallResult with Event == Call Relative to the inner scope_parent 
                2. TraceCallResult with Event == Line Relative to the inner scope_parent
            """

            return self.list_trace_call_result[0]
        elif self.interpretable_type == constants.Event.CALL:
            """
            Recall that the 1st index TraceCallResult is the call
            
            In self._list_trace_call_result_raw by index:
                0. TraceCallResult Event == Call
            """

            return self.list_trace_call_result[0]
        elif self.interpretable_type == constants.Event.LINE:
            return self.list_trace_call_result[0]

        raise NoTraceCallResult("Primary TraceCallResult could be returned. This exception happened because something "
                                "was not handled in this function where this exception was raised.")

    def pop_trace_call_result(self) -> _trace_call_result.TraceCallResult:
        """
        Pop to get the most recent TraceCallResult object from this interpretable

        :return:
        """
        return self.list_trace_call_result.pop()

    def __str__(self):
        trace_call_result = self.get_trace_call_result_primary()

        ####################
        # DEBUGGING START
        ####################

        # print(f"INDEX LEVEL CORRECTED: {}\nINDEX LEVEL OFFSET: {}\n".format(
        #     trace_call_result.get_indent_level_corrected(),
        #     self.scope_parent.get_indent_level_first()
        # ))

        ####################
        # DEBUGGING END
        ####################

        return f"{str(trace_call_result)} | {self.dict_k_variable_v_value}"

    def __hash__(self):
        """
        Since interpretables are pretty much based on the their primary TraceCallResult object,
        use it's hash. If the above statement is true, the only difference between Interpretable
        objects will be their self.dict_k_variable_v_value if assigned

        :return:
        """

        return self.get_trace_call_result_primary().__hash__()

    def __eq__(self, other):
        """

        :param other:
        :return:
        """
        return self.__hash__()

    def get_scope_parent(self) -> scope.Scope:
        return self.scope_parent

    def get_interpretable_type(self) -> Union[constants.InterpretableType, None]:
        return self.interpretable_type