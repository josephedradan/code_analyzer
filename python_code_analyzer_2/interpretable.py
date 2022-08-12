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

from python_code_analyzer_2 import constants
from python_code_analyzer_2 import scope
from python_code_analyzer_2 import trace_call_result


class Interpretable:

    def __init__(self, scope_parent: scope.Scope, interpretable_type: Union[constants.InterpretableType,
                                                                            None] = None):

        self.scope: scope.Scope = scope_parent

        self.scope._add_interpretable(self)  # Immediately add self to the scope

        self.interpretable_type: Union[constants.Event, None] = interpretable_type

        ####################

        # All TraceCallResult objects related to this interpretable
        self.list_trace_call_result: List[trace_call_result.TraceCallResult] = []

        # Recorded "Variable: Value" pairs
        self.dict_k_variable_v_value: Dict[str, Any] = {}

        ####################

        # TODO DELETE
        # Dictionary that contains key value pairs for the current trace_call_result
        # self.dict_k_variable_v_value: Dict[str, Any] = {}

    def set_interpretable_type(self, interpretable_type: constants.Event):
        self.interpretable_type = interpretable_type

    def get_list_trace_call(self) -> List[trace_call_result.TraceCallResult]:
        return self.list_trace_call_result

    def add_trace_call_result(self, trace_call_result: trace_call_result.TraceCallResult):
        """

        Notes:
            Should not be called from python_code_analyzer


        """
        trace_call_result.assign_interpretable(self)

        self.list_trace_call_result.append(trace_call_result)

    def update_dict_k_variable_v_value_through_list(self, list_dict_k_variable_v_value: List[Dict[str, Any]]):
        while list_dict_k_variable_v_value:
            self.update_dict_k_variable_v_value(list_dict_k_variable_v_value.pop())

    def update_dict_k_variable_v_value(self, dict_k_variable_v_value: Dict[str, Any]):
        self.dict_k_variable_v_value.update(dict_k_variable_v_value)

    def get_dict_k_variable_v_value(self) -> Dict[str, Any]:
        return self.dict_k_variable_v_value

    def get_trace_call_result_primary(self) -> trace_call_result.TraceCallResult:

        if not self.list_trace_call_result:
            raise Exception(f"No {trace_call_result.TraceCallResult.__name__} objects in interpretable")

        trace_call_result_first = self.list_trace_call_result[0]

        trace_call_result_last = self.list_trace_call_result[-1]

        python_key_word = trace_call_result_first.get_python_key_word()

        # print("------", *[f"\"{i}\"" for i in self.list_trace_call_result])

        # if len(self.list_trace_call_result) == 1:
        #     return self.list_trace_call_result[0]
        # elif python_key_word == constants.CLASS:
        #     return self.list_trace_call_result[0]
        # elif python_key_word == constants.RETURN:
        #     return self.list_trace_call_result[-1]

        if self.interpretable_type == constants.Event.RETURN:
            return self.list_trace_call_result[1]
        elif self.interpretable_type == constants.Keyword.CLASS:
            """
            Recall that this is the definition of the class not the call of it.
            Note that the 0th index TraceCallResult is relative to the outer scope 
            """
            return self.list_trace_call_result[0]
        elif self.interpretable_type == constants.Event.CALL:

            """
            Recall that the 1st index TraceCallResult is the call 
            """
            return self.list_trace_call_result[0]
        elif self.interpretable_type == constants.Event.LINE:
            return self.list_trace_call_result[0]

        raise Exception("JOSEPH SOMETHING WENT WRONG")

    def pop_trace_call_result(self) -> trace_call_result.TraceCallResult:
        return self.list_trace_call_result.pop()

    def __str__(self):
        trace_call_result = self.get_trace_call_result_primary()

        # print(f"LEVEL CORRECT: {trace_call_result.get_indent_level_corrected()} LEVEL OFFSET: {self.scope.get_index_level_start()}")

        return f"{str(trace_call_result)} {self.dict_k_variable_v_value}"
