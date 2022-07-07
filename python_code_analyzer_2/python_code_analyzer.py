"""
Created by Joseph Edradan
Github: https://github.com/josephedradan

Date created: 5/21/2022

Purpose:

Details:

Description:

Notes:
    Abusing settrace

IMPORTANT NOTES:

Explanation:

Tags:

Reference:
    What cool hacks can be done using sys.settrace?
        Notes:
            Old stuff about settrace.
            Callgraph uses this
                https://pycallgraph.readthedocs.io/en/master/
        Reference:
            https://stackoverflow.com/questions/1692866/what-cool-hacks-can-be-done-using-sys-settrace
"""
import sys
from functools import wraps
from typing import Union, List, Dict, Any, Callable, Type

from python_code_analyzer_2 import constants
from python_code_analyzer_2.interpretable import Interpretable
from python_code_analyzer_2.trace_call_result import TraceCallResult
from python_code_analyzer_2.scope import Scope

old_trace = sys.gettrace()

"""
Notes (format later):

    https://docs.python.org/3/library/sys.html
    
    frame:
        is the current stack frame
    
    event:
        can be:
        'call', 'line', 'return', 'exception' or 'opcode'
    
    arg:
        depends on the event type

"""

from types import TracebackType, FrameType



class _Special:
    __slots__ = ()
    pass


class _SpecialStop(_Special):
    __slots__ = ()
    """
    A Unique object that only exists in this file used for identifying some certain condition because
    the traceback function's call is limited in doing very specific trace_call_results. Some limitations of the
    traceback function are: 
        Getting only the line of code of a callable being called or the callable's definition rather 
        than the callable object itself.
    """
    pass


_SPECIAL_STOP = _SpecialStop()


def _decorator_ignore_trace_call_result(callable_given: Union[Callable, None] = None) -> Callable:
    """
    This decorator makes the trace function ignore creating TraceCallResult objects for callables that have this
    decorator on them

    Notes:
        Apply decorator to a callable to ignore probably all the possibilities of TraceCallResult objects being
        created from within that callable including the callable itself.

        Basically, ignore trace_call_result objects being created from a callable if this decorator is on that object

    :param callable_given:
    :return:
    """

    def decorator_actual(callable_given_inner: Callable) -> Callable:
        @wraps(callable_given_inner)
        def wrapper(*args, **kwargs):
            python_code_analyzer_instance = args[0]

            if not isinstance(python_code_analyzer_instance, PythonCodeAnalyzer):
                raise Exception(f"First argument of the function must be of type {PythonCodeAnalyzer.__name__}")

            python_code_analyzer_instance._special_stop = True

            result = callable_given_inner(*args, **kwargs)

            python_code_analyzer_instance._special_stop = False

            return result

        return wrapper

    return decorator_actual(callable_given) if callable_given else decorator_actual


# class _ContainerDict:
#
#     def __init__(self,
#                  dict_k_variable_v_value_for_trace_call_result_next: Dict[str, Any],
#                  scope_depth_callable: int):
#
#         self.dict_k_variable_v_value_for_trace_call_result_next = dict_k_variable_v_value_for_trace_call_result_next
#         self.scope_depth_callable = scope_depth_callable

class _List(list):
    def pop(self, __index: int = ...):
        print(super(_List, self).pop())


class PythonCodeAnalyzer:

    def __init__(self):

        ##########
        """
        Internal Variables
        
        These variables are special and should not be used or seen outside this object
        """

        global _SPECIAL_STOP

        self._special_stop: _Special = _SPECIAL_STOP

        self.__scope_level_self: int = 0

        self._trace_call_result_possible_on_board: Union[TraceCallResult, None] = None

        # What python stack frame index the trace function has encountered
        # self._scope_level_by_application: int = 0

        ##
        """
        Traceback frame class
        
        """
        self._dict_k_object_v_trace_call_result_class: Dict[Type[object], TraceCallResult] = {}  # TODO NOT USED

        # self._trace_call_result_possible_on_board_event_line_for_class: Union[TraceCallResult, None] = None
        #
        # self._trace_call_result_possible_on_board_event_call_for_class: Union[TraceCallResult, None] = None

        ##

        self._scope_level_class = 0

        ##

        self.bool_record_dict_k_variable_v_value_for_trace_call_result_next: bool = False

        self.list_dict_k_variable_v_value_for_trace_call_result_next: List[Dict[str, Any]] = []

        ##
        """
        The below variables are unnecessary
        """

        # self.bool_record_dict_k_variable_v_value_for_trace_call_result_previous: bool = False
        #
        # self.list_dict_k_variable_v_value_for_trace_call_result_previous: List[Dict[str, Any]] = []

        ####################

        """
        Due to this function hijacking the current trace function, the below code will
        store the original trace function to a variable which will then be used to restore the trace function
        """
        self._trace_function_old: Union[TracebackType, None] = None

        ################################################################################

        # List of all the trace_call_results
        self.list_trace_call_result: List[TraceCallResult] = []

        ##

        self.list_interpretable: List[Interpretable] = []

        self.interpretable_current: Union[Interpretable, None] = None

        ##

        self.list_stack_scope_container: List[Scope] = []

        scope_container_initial: Scope = Scope()

        self.list_stack_scope_container.append(scope_container_initial)

        ##








    def decorator_ignore_callable(self, callable_given: Union[Callable, None] = None) -> Callable:
        """
        This decorator makes the trace function ignore creating TraceCallResult objects for callables that have this
        decorator on them

        Notes:
            Apply decorator to a callable to ignore probably all the possibilities of TraceCallResult objects being
            created from within that callable including the callable itself.

            Basically, ignore trace_call_result objects being created from a callable if this decorator is on that object

        :param callable_given:
        :return:
        """

        # return _decorator_ignore_trace_call_result(callable_given)

        def decorator_actual(callable_given_inner: Callable) -> Callable:
            @wraps(callable_given_inner)
            def wrapper(*args, **kwargs):
                nonlocal self
                # self.__scope_level_self -= 1

                # self._trace_what_has_been_called = False

                result = callable_given_inner(*args, **kwargs)

                # self._trace_what_has_been_called = True
                # self.__scope_level_self += 1
                return result

            return wrapper

        return decorator_actual(callable_given) if callable_given else decorator_actual

    def start(self):
        """
        Replace the trace function with a custom trace function that records the lines of python code that can be
        interpreted

        :return:
        """

        def trace_function_callback(frame: FrameType, event: str, arg):
            """

            :param frame:
            :param event:
            :param arg:
            :return:
            """

            # TODO ALSO USE ORIGINAL TRACE FUNCTION AS A AN OPTION

            nonlocal self

            # filename_raw: str = frame.f_code.co_filename

            # TODO LOOK AT THIS
            # if filename_raw.startswith('<'):return

            # TODO LOOK AT THIS
            # if not filename_raw.is_relative_to(base_dir := Path()):return

            """
            THE SELF CAN BE ANY SELF IN THE SCOPE, BUT IF THE SELF IS FROM THIS OBJECT THEN WE HAVE SOMETHING SPECIAL
            
            Notes:
                There can only be one self in the local scope
            """
            self_from_frame_locals: Union[PythonCodeAnalyzer, None] = frame.f_locals.get("self")

            _stop_object: Union[_SpecialStop, None] = frame.f_locals.get("____stop____")

            scope_container_top: Scope = self.list_stack_scope_container[-1]


            print("-" * 10)
            print(frame)
            print(frame.f_locals)

            trace_call_result_possible_temp: TraceCallResult = TraceCallResult(
                frame,
                event,
                arg,
                self._get_scope_level_by_application()
            )
            print(event)
            print(f"LINE {frame.f_lineno} {trace_call_result_possible_temp.code_line} ")

            callable_name = frame.f_code.co_name

            if event == constants.RETURN:
                """
                A function (or other code block) is about to return. The local trace function is called; arg is the 
                value that will be returned, or None if the event is caused by an exception being raised. 
                The trace function’s return value is ignored.
                
                """

                ##########

            elif event == constants.CALL:
                """
                A function is called (or some other code block entered). The global trace function is called; 
                arg is None; the return value specifies the local trace function.
                
                """
                # data = filename_raw.relative_to(frame.f_lineno, frame.f_code.co_name, depth)

                # TODO REMOVE THE BELOW
                # data = (filename, callable_line_number, callable_name, self._get_scope_level_by_application())

                # self._list_frame.append(data)

                if self_from_frame_locals is self:

                    """
                    When any of the methods of this object is called within code that is being analyzed, an e
                    vent == LINE is called as a an argument to this method which corresponds to one of this object's 
                    methods. Due to the any of this object's methods being ignored by default when code is being 
                    analyzed, the call that had event == LINE should not be seen by the user because it serves no
                    purpose to the actual code being analyzed. 

                    Basically, remove the trace_call_result that indicates the existence of any of this object's 
                    methods being called because it's unrelated to the code that this object should be analyzing.
                    """

                    """
                    The popped trace_call_result should have an event of LINE and is the call to a method from this object
                    whose trace_call_result has nothing to do with the analysis of what this object should be analyzing.
                    
                    Notes:
                        If in code being analyzed calls a method of this object
                            1.  The callback will be called which will add the the method call as an trace_call_result
                            2.  The next callback will be the same as the 1. but the event will be call, BUT self will 
                                be in f_locals meaning the trace_call_result will not be made.
                            3.  Since the method call in the code is unrelated the analysis of the code, the most
                                recently added trace_call_result will be dropped.                        
                        
                    """
                    if self.list_trace_call_result and _stop_object is None and self.__scope_level_self == 0:
                        trace_call_result_possible = self.list_trace_call_result.pop()
                        print("POPPING 1", trace_call_result_possible, event)

            elif event == constants.LINE:
                """
                The interpreter is about to execute a new line of code or re-execute the condition of a loop. 
                The local trace function is called; arg is None; the return value specifies the new local 
                trace function. See Objects/lnotab_notes.txt for a detailed explanation of how this works.
                Per-line events may be disabled for a frame by setting f_trace_lines to False on that frame.
                
                """
                pass

            elif event == constants.EXCEPTION:
                """
                An exception has occurred. The local trace function is called; arg is a 
                tuple (exception, value, traceback); the return value specifies the new local trace function.
                """
                pass

            elif event == constants.OPCODE:
                """
                The interpreter is about to execute a new opcode (see dis for opcode details). The local trace 
                function is called; arg is None; the return value specifies the new local trace function. 
                Per-opcode events are not emitted by default: they must be explicitly requested by setting 
                f_trace_opcodes to True on the frame.
                """
                pass

            trace_call_result_possible: Union[TraceCallResult, None] = None

            # # If the frame and event (possible trace_call_result) should be recorded
            # if self._trace_what_has_been_called is True:

            # If the frame's local's self is not this object
            if self_from_frame_locals is not self and self.__scope_level_self == 0:

                # """
                # The below condition deals with determining if the previous trace_call_result is unrelated to this
                # current traceback call's handling of a frame that involves self.
                #
                # Basically, if self._trace_call_result_possible_on_board is an trace_call_result, and the the current
                # frame/event/arg has a relationship to this object (self) then
                # exhaust self.list_dict_k_variable_v_value_for_trace_call_result_next to
                # self._trace_call_result_possible_on_board because it's an trace_call_result that this application
                # considers to be an proper trace_call_result
                # """
                # if self._trace_call_result_possible_on_board is not None:
                #     self._trace_call_result_possible_on_board.exhaust_list_dict_k_variable_v_value(
                #         self.list_dict_k_variable_v_value_for_trace_call_result_next
                #     )
                #
                #     self._trace_call_result_possible_on_board = None
                #
                # """
                # This trace_call_result is considered "possible" because code that uses this object will be
                # shown to this traceback function's call which has nothing to do with the code being analyzed.
                #
                # Basically, if code that is being analyzed has any calls to this object's methods, then that
                # trace_call_result created is analyzing this object which is wrong which is why the variable is
                # called trace_call_result_possible
                # """




                trace_call_result_possible = TraceCallResult(
                    frame,
                    event,
                    arg,
                    self._get_scope_level_by_application(),
                )



                """
                The below condition pops the trace_call_result at the top and steals its dict_k_variable_v_value
                and adds it to the recently created trace_call_result because the popped trace_call_result is the same at
                the recently created trace_call_result, but the recently created trace_call_result has it's event == RETURN
                
                Notes:
                    You want to have the trace_call_result with event == RETURN because this function's argument "arg" 
                    can be the return result of this callable. 
                """
                if event == constants.RETURN:
                    trace_call_result_event_line_before_event_return = self.list_trace_call_result.pop()

                    print("POPPING 2", trace_call_result_event_line_before_event_return)

                    dict_k_variable_v_value_temp = trace_call_result_event_line_before_event_return.get_dict_k_variable_v_value()

                    trace_call_result_possible.update_dict_k_variable_v_value(dict_k_variable_v_value_temp)

                ##

                if trace_call_result_possible.get_python_key_word() == constants.CLASS:

                    if (trace_call_result_possible.get_event() == constants.LINE and
                            self._trace_call_result_possible_on_board_event_line_for_class is None):

                        self._trace_call_result_possible_on_board_event_line_for_class = trace_call_result_possible

                    elif (trace_call_result_possible.get_event() == constants.CALL and
                          self._trace_call_result_possible_on_board_event_call_for_class is None):

                        self._trace_call_result_possible_on_board_event_call_for_class = trace_call_result_possible

                    elif (self._trace_call_result_possible_on_board_event_line_for_class is not None and
                          self._trace_call_result_possible_on_board_event_call_for_class is not None):

                        # trace_call_result_event_line_for_class = self.list_trace_call_result.pop()  # Has access to local variables when defined
                        # trace_call_result_event_call_for_class = self.list_trace_call_result.pop()  # Same as previous frame but the event is "call"


                        # scope_container_top.pop() # NOT A DOUBLE POP
                        # scope_container_top.pop()


                        # Because the most recent trace_call_result has an event of "call"
                        # trace_call_result_possible.get_scope_level_container_by_application().scope_level = self._get_scope_level_by_application() - 1

                        # print("POPPING 3", trace_call_result_event_line_for_class, trace_call_result_event_call_for_class)

                        self._scope_level_class += 1

                        self._trace_call_result_possible_on_board_event_line_for_class = None
                        self._trace_call_result_possible_on_board_event_call_for_class = None

                    else:
                        self._trace_call_result_possible_on_board_event_line_for_class = None
                        self._trace_call_result_possible_on_board_event_call_for_class = None


                #########
                # UGGG
                #########

                if event == constants.CALL:

                    # if self_from_frame_locals is self: // TODO DO NOT USE THIS HERE
                    #     self.__scope_level_self += 1

                    if self.__scope_level_self <= 0:

                        scope_depth_index = len(self.list_stack_scope_container)

                        # TODO: THIS IS TO CORRECT THE CLASS CALLING WHEN MAKIGN A CLASS
                        # if trace_call_result_possible.get_python_key_word() == constants.CLASS:
                        #     scope_depth_index += -1

                        from joseph_library.print import print_blue, print_magenta
                        print_blue(f"SCOPE DEPTH: {scope_depth_index}")

                        trace_call_result_top_level_corrected = 0

                        if self.list_trace_call_result:
                            trace_call_result_top_level_corrected = self.list_trace_call_result[-1].get_scope_level_corrected()


                        scope_container_new: Scope = Scope(
                            trace_call_result_top_level_corrected,
                            scope_depth_index,
                            scope_container_top
                        )
                        print_magenta("NEW SCOPE")
                        self.list_stack_scope_container.append(scope_container_new)

                scope_container_top: Scope = self.list_stack_scope_container[-1]  # REASSIGN

                ##########
                # ASSIGNING THE PREVIOUS INTERPRETABLES TO THE possible TraceCallResult
                ##########

                # TODO FIX TEH POPPING PROBLEM
                trace_call_result_from_scope_container_top: Union[TraceCallResult, None] = scope_container_top.get_trace_call_result_top()

                trace_call_result_possible.set_trace_call_result_previous_by_scope(trace_call_result_from_scope_container_top)

                ##

                trace_call_result_previous_direct = None

                if self.list_trace_call_result:
                    trace_call_result_previous_direct = self.list_trace_call_result[-1]

                trace_call_result_possible.set_trace_call_result_previous_by_direct(trace_call_result_previous_direct)


                ##

                self._trace_call_result_possible_on_board = trace_call_result_possible

                self.list_trace_call_result.append(trace_call_result_possible)  # THIS IS THE MAIN ADD

                ##

                scope_container_top.add_trace_call_result(trace_call_result_possible)


                #####

                if event == constants.RETURN:
                    if self._scope_level_class > 0:
                        # This will remove the return when a class is being defined
                        trace_call_result_event_line_for_class = self.list_trace_call_result.pop()

                        print("POPPING 4", trace_call_result_event_line_for_class)

                        self._scope_level_class -= 1

            # If the current call to this function was from this object
            elif self_from_frame_locals is self:
                self._trace_call_result_possible_on_board = None

            ##########
            # ENDING STUFF
            ##########

            if event == constants.RETURN:
                print("LAST RETURN", self.__scope_level_self)
                # self._scope_level_by_application -= 1  # TODO REMOVE

                if self_from_frame_locals is self:
                    self.__scope_level_self -= 1

                elif self.__scope_level_self <= 0:

                    self.list_stack_scope_container.pop()


            elif event == constants.CALL:

                # self._scope_level_by_application += 1  # TODO CAN BE MOVED TO THE TOP event == CALL STATEMENT // TODO REMOVE

                ##

                if self_from_frame_locals is self:
                    self.__scope_level_self += 1

                # elif self.__scope_level_self <= 0:
                #
                #     scope_depth_index = len(self.list_stack_scope_container)
                #
                #     # TODO: THIS IS TO CORRECT THE CLASS CALLING WHEN MAKIGN A CLASS
                #     if trace_call_result_possible.get_python_key_word() == constants.CLASS:
                #         scope_depth_index += -1
                #
                #     from joseph_library.print import print_blue, print_magenta
                #     print_blue(f"SCOPE DEPTH: {scope_depth_index}")
                #
                #     scope_container_new: Scope = Scope(
                #         scope_depth_index,
                #         scope_depth_index,
                #         scope_container_top
                #     )
                #     print_magenta("NEW SCOPE")
                #     self.list_stack_scope_container.append(scope_container_new)


            ############
            # ENDING CALLS HERE
            ###########


            print("-" * 10)
            return trace_function_callback

        sys.settrace(trace_function_callback)

    # @_decorator_ignore_trace_call_result
    def stop(self, ____stop____=_SPECIAL_STOP) -> None:
        """
        Restores the old trace function

        :param ____stop____: This variable is required and should not be changed as it allows the traceback function
        to acknowledge a special condition that can only be communicated via default argument.
        :return:
        """
        # print("STOP")
        sys.settrace(self._trace_function_old)

    def _get_scope_level_by_application(self) -> int:  # TODO REMOVE
        return len(self.list_stack_scope_container)

    def record_dict_for_trace_call_result_next(self, dict_k_variable_v_value: Dict[str, Any]) -> None:
        """
        Update update_dict_k_variable_v_value for trace_call_result_current (the next trace_call_result) by appending the
        dict to a list that will then be exhausted into the next trace_call_result which will be trace_call_result_current

        :param dict_k_variable_v_value:
        :return:
        """

        self.list_dict_k_variable_v_value_for_trace_call_result_next.append(dict_k_variable_v_value)

    def record_dict_for_trace_call_result_previous(self, dict_k_variable_v_value: Dict[str, Any]) -> None:
        """
        Update update_dict_k_variable_v_value for trace_call_result_previous

        :param dict_k_variable_v_value:
        :return:
        """
        if self.list_stack_scope_container:
            trace_call_result_previous_by_scope = self.list_stack_scope_container[-1].get_trace_call_result_top()

            if trace_call_result_previous_by_scope is not None:

                from joseph_library.print import print_cyan, print_blue
                print("FUJA")
                print_cyan(trace_call_result_previous_by_scope)
                print_blue(dict_k_variable_v_value)
                print("FUJB")
                trace_call_result_previous_by_scope.update_dict_k_variable_v_value(dict_k_variable_v_value)




        # for trace_call_result in reversed(self.list_trace_call_result):
        #     print("---- LOOK ----", trace_call_result.get_scope_level_container_by_application(),
        #           self._get_scope_level_by_application())
        #
        #     if trace_call_result.get_scope_level_container_by_application() == self._scope_level_by_application - 1:
        #         trace_call_result.update_dict_k_variable_v_value(dict_k_variable_v_value)
        #         break

        """
        Old way which adds directly to the previous trace_call_result. The problem was that the top trace_call_result
        could have been part of a chain of trace_call_results such as from a function call which would lead to
        adding the dict to the return trace_call_result which was part of the chain of trace_call_results.
        """
        # if self.list_trace_call_result:
        #     self.list_trace_call_result[-1].update_dict_k_variable_v_value(dict_k_variable_v_value)

    def print(self):
        print("#" * 100)
        for trace_call_result in self.list_trace_call_result:
            print(trace_call_result)
            print()
