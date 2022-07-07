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
from typing import Dict, Any, List

from python_code_analyzer_2 import constants
from python_code_analyzer_2.scope import Scope
from python_code_analyzer_2.trace_call_result import TraceCallResult


class Interpretable():

    def __init__(self, scope_parent: Scope):

        self.scope_parent: Scope = scope_parent

        ##########

        self.list_trace_call_result: List[TraceCallResult] = []

        ####################

        # Dictionary that contains key value pairs for the current trace_call_result
        self.dict_k_variable_v_value: Dict[str, Any] = {}

    def add_trace_call_result(self, trace_call_result: TraceCallResult):
        self.list_trace_call_result.append(trace_call_result)

    def update_dict_k_variable_v_value(self, dict_k_variable_v_value: Dict[str, Any]):
        self.dict_k_variable_v_value.update(dict_k_variable_v_value)

    def get_dict_k_variable_v_value(self) -> Dict[str, Any]:
        return self.dict_k_variable_v_value

    def get_trace_call_result_primary(self) -> TraceCallResult:

        if not self.list_trace_call_result:
            raise Exception(f"No {TraceCallResult.__name__} objects in interpretable")

        trace_call_result_first = self.list_trace_call_result[0]

        trace_call_result_last = self.list_trace_call_result[-1]

        python_key_word = trace_call_result_first.get_python_key_word()

        if len(self.list_trace_call_result) == 1:
            return self.list_trace_call_result[0]
        elif python_key_word == constants.CLASS:
            return self.list_trace_call_result[0]
        elif python_key_word == constants.RETURN:
            return self.list_trace_call_result[-1]

        raise Exception("JOSEPH SOMETHING WENT WRONG")
