"""
Created by Joseph Edradan
Github: https://github.com/josephedradan

Date created: 5/21/2022

Purpose:

Details:

Description:

Notes:
    Abusing settrace

    Design:



    Note that The order of TraceCallResult objects is
        Line
        Call
        Actual code execution of what was for the Call Event




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
from enum import Enum, auto
from functools import wraps
from typing import Union, List, Dict, Any, Callable, Type

from python_code_analyzer_2 import constants
from python_code_analyzer_2.interpretable import Interpretable
from python_code_analyzer_2.scope import Scope
from python_code_analyzer_2.trace_call_result import TraceCallResult

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
    class Command(Enum):
        """
        Special commands that are only by the parent class to do specific actions

        """
        STOP = auto()
        ADD_DICT_FOR_INTERPRETABLE_NEXT = auto()
        ADD_DICT_FOR_INTERPRETABLE_PREVIOUS = auto()

    def __init__(self):

        ##########
        """
        Internal Variables
        
        These variables are special and should not be used or seen outside this object
        """

        global _SPECIAL_STOP

        self._special_stop: _Special = _SPECIAL_STOP

        self.__scope_level_self: int = 0  # USED TO DETERMINE IF STILL INSIDE OF SELF DOING SOMECALL NOT FROM THIS OBJECT

        self._trace_call_result_possible_on_board: Union[TraceCallResult, None] = None

        # What python stack frame index the trace function has encountered
        # self._scope_level_by_application: int = 0

        ##
        """
        Traceback frame class
        
        """
        self._dict_k_object_v_trace_call_result_class: Dict[Type[object], TraceCallResult] = {}  # TODO NOT USED

        ##

        ##

        self.bool_record_dict_k_variable_v_value_for_trace_call_result_next: bool = False

        self.list_dict_k_variable_v_value_for_trace_call_result_next: List[Dict[str, Any]] = []


        self.list_dict_k_variable_v_value_for_trace_call_result_pervious: List[Dict[str, Any]] = []

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

        ####################

        self._list_command: List[PythonCodeAnalyzer.Command] = []


        ################################################################################

        # List of all the trace_call_results
        self.list_trace_call_result: List[TraceCallResult] = []

        ##

        self.list_interpretable: List[Interpretable] = []

        self.interpretable_current: Union[Interpretable, None] = None

        ##

        self.list_stack_scope: List[Scope] = []

        #####

        scope_container_initial: Scope = Scope()

        self.list_stack_scope.append(scope_container_initial)

        ##########
        """
        INTERPRETABLE CLASS VARIABLES  
        """
        self._trace_call_result_possible_on_board_event_line_for_class: Union[TraceCallResult, None] = None

        self._trace_call_result_possible_on_board_event_call_for_class: Union[TraceCallResult, None] = None

        """
        INTERPRETABLE RETURN VARIABLES

        """

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

            scope_current: Scope = self.list_stack_scope[-1]

            interpretable_current: Union[Interpretable, None] = (
                self.list_interpretable[-1] if self.list_interpretable else None
            )

            trace_call_result_current: Union[TraceCallResult, None] = (
                self.list_trace_call_result[-1] if self.list_trace_call_result else None
            )

            print("-" * 10)
            print("frame:", frame)
            print("frame.locals:", frame.f_locals)
            print("event:", event)
            print("self:", self_from_frame_locals)
            # print("trace_call_result_current", trace_call_result_current)
            """
            If not self related (Analyzing the code)
            
            Notes:
                Everything inside the if statement relates to the code be analyzed
            
            """
            if self_from_frame_locals is not self and self.__scope_level_self == 0:

                scope_depth_index = len(self.list_stack_scope)

                ####################
                # SCOPE STUFF
                ####################
                if event == constants.Event.CALL.value:
                    trace_call_result_top_level_corrected = 1  # THIS SHOULD BE 1 BECAUSE A SCOPE IS ALWAYS 1 LEVEL DEEPER

                    # Recall that trace_call_result_current is the previous interpretable
                    if trace_call_result_current is not None:
                        trace_call_result_top_level_corrected += trace_call_result_current.get_indent_level_corrected()

                        print("INSIDE YO, STARTING LEVEL IS", trace_call_result_top_level_corrected, "ADDED WAS",
                              trace_call_result_current.get_indent_level_corrected())

                    from joseph_library.print import print_blue, print_magenta
                    print_blue(f"SCOPE DEPTH BY CONDITIONAL: {scope_depth_index}")

                    print_magenta(f"LEVEL CORRECTED {trace_call_result_top_level_corrected}")

                    scope_new: Scope = Scope(
                        trace_call_result_top_level_corrected,
                        scope_depth_index,
                        scope_current
                    )

                    print_magenta("NEW SCOPE")
                    print_magenta("trace_call_result_top_level_corrected", trace_call_result_top_level_corrected)

                    self.list_stack_scope.append(scope_new)

                elif event == constants.Event.RETURN.value:
                    # May need to add stuff here eventually if needed
                    pass

                ####################
                # TraceCallResult
                ####################

                trace_call_result_new = TraceCallResult(
                    frame,
                    event,
                    arg,
                    self._get_scope_level_by_application(),
                )

                ####################
                # Interpretable RETURN
                ####################
                if event == constants.Event.RETURN.value:
                    """ 
                    Notes:
                        Order:
                            1. Line Relative to the inner scope
                            2. Return Relative to the inner scope
                            
                        Add trace_call_result_new to interpretable_current (Adding to interpretable_current is default
                        behavior)
                    """
                    interpretable_current.set_interpretable_type(constants.Event.RETURN)

                    from joseph_library.print import print_blue, print_magenta
                    print_blue("RETURN HIT")

                    self.list_stack_scope.pop()  ## FIXME NOT YET

                ####################
                # Interpretable CLASS
                ####################
                elif trace_call_result_new.get_python_key_word() == constants.Keyword.CLASS:
                    """
                    Notes:
                        Order:
                            1. Line Relative to the outer scope
                            2. Call Relative to the inner scope
                            3. Line Relative to the inner scope
                    
                        For a correct class you need:
                            _trace_call_result_possible_on_board_event_line_for_class
                            _trace_call_result_possible_on_board_event_call_for_class
                    """

                    # First trace_call_result
                    if (trace_call_result_new.get_event() == constants.Event.LINE and
                            self._trace_call_result_possible_on_board_event_line_for_class is None):

                        # Replace interpretable_current with a new one
                        interpretable_current = Interpretable(scope_current, constants.Keyword.CLASS)
                        self.list_interpretable.append(interpretable_current)

                        self._trace_call_result_possible_on_board_event_line_for_class = trace_call_result_new
                        print("CLASS ASS 1")

                    # Second trace_call_result
                    elif (trace_call_result_new.get_event() == constants.Event.CALL and
                          self._trace_call_result_possible_on_board_event_call_for_class is None):

                        self._trace_call_result_possible_on_board_event_call_for_class = trace_call_result_new
                        print("CLASS ASS 2")

                    # Third trace_call_result
                    elif (self._trace_call_result_possible_on_board_event_line_for_class is not None and
                          self._trace_call_result_possible_on_board_event_call_for_class is not None):

                        print("CLASS ASS 3")

                        self._trace_call_result_possible_on_board_event_line_for_class = None
                        self._trace_call_result_possible_on_board_event_call_for_class = None

                    # IF THE ASSUMPTION FOR CREATING A INTERPRETABLE CLASS WAS INCORRECT, THIS IS THE FALL BACK
                    else:

                        # Pop the TODO NO POPPING
                        # scope_current.pop_interpretable()
                        # self.list_interpretable.pop()

                        if self._trace_call_result_possible_on_board_event_line_for_class is not None:
                            interpretable_temp = Interpretable(scope_current)
                            self.list_interpretable.append(interpretable_temp)

                            interpretable_temp.add_trace_call_result(
                                self._trace_call_result_possible_on_board_event_line_for_class
                            )

                        if self._trace_call_result_possible_on_board_event_call_for_class is not None:
                            interpretable_temp = Interpretable(scope_current)
                            self.list_interpretable.append(interpretable_temp)

                            interpretable_temp.add_trace_call_result(
                                self._trace_call_result_possible_on_board_event_call_for_class
                            )

                        self._trace_call_result_possible_on_board_event_line_for_class = None
                        self._trace_call_result_possible_on_board_event_call_for_class = None

                ####################
                # Interpretable CALL
                ####################
                elif event == constants.Event.CALL.value:  # Notice that the value of the Enum is compared
                    """
                    Notes:
                        Order:
                            1. Line relative to outer scope
                            2. Call relative to inner scope
                    
                    """

                    # TODO: THIS IS TO CORRECT THE CLASS CALLING WHEN MAKIGN A CLASS
                    # if trace_call_result_new.get_python_key_word() == constants.CLASS:
                    #     scope_depth_index += -1

                    #############
                    # from joseph_library.print import print_blue, print_magenta
                    # print_blue(f"SCOPE DEPTH BY CONDITIONAL: {scope_depth_index}")
                    # trace_call_result_top_level_corrected = 1  # THIS SHOULD BE 1 BECAUSE A SCOPE IS ALWAYS 1 LEVEL DEEPER
                    #
                    #
                    # # Recall that trace_call_result_current is the previous interpretable
                    # if trace_call_result_current is not None:
                    #     trace_call_result_top_level_corrected += trace_call_result_current.get_indent_level_corrected()
                    #
                    #     print("INSIDE YO, STARTING LEVEL IS", trace_call_result_top_level_corrected, "ADDED WAS", trace_call_result_current.get_indent_level_corrected())
                    #
                    # print_magenta(f"LEVEL CORRECTED {trace_call_result_top_level_corrected}")
                    # scope_new: Scope = Scope(
                    #     trace_call_result_top_level_corrected,
                    #     scope_depth_index,
                    #     scope_current
                    # )
                    #
                    # print_magenta("NEW SCOPE")
                    # print_magenta("trace_call_result_top_level_corrected", trace_call_result_top_level_corrected)
                    #
                    # self.list_stack_scope.append(scope_new)

                    #############

                    #####
                    # SETTING THE INTERPRETABLE'S TYPE
                    interpretable_current = Interpretable(scope_current, constants.Event.CALL)
                    self.list_interpretable.append(interpretable_current)

                    # trace_call_result_top = scope_current.get_interpretable_top()  # FIXME DELETE ME
                    #
                    # scope_level_by_analyzer = len(self.list_stack_scope)
                    #
                    # scope_new = Scope(
                    #     trace_call_result_current.get_indent_level_by_code_execution(),
                    #     scope_level_by_analyzer,
                    #     scope_current
                    # )
                    #
                    # self.list_stack_scope.append(scope_new)

                ####################
                # Interpretable (DEFAULT)
                ####################
                else:
                    """
                    Notes:
                        Order:
                            1. Line
                    """
                    # Replace interpretable_current with a new one
                    interpretable_current = Interpretable(scope_current, constants.Event.LINE)
                    self.list_interpretable.append(interpretable_current)

                #####
                # EXHAUSTING TO INTERPRETABLE NEXT

                interpretable_current.update_dict_k_variable_v_value_through_list(
                    self.list_dict_k_variable_v_value_for_trace_call_result_next
                )

                #####

                ############
                # PRIMARY ZONE
                ############

                interpretable_current.add_trace_call_result(trace_call_result_new)

                # CORRECTING THE INDENT LEVEL FOR EVENTS THAT ARE CALLS
                if trace_call_result_current is not None and event == constants.Event.CALL.value:
                    indent_level_offset = (
                            trace_call_result_current.get_indent_level_relative() -
                            trace_call_result_new.get_indent_level_relative()
                    )

                    trace_call_result_new.set_indent_level_offset(indent_level_offset)

                print(f"LINE {frame.f_lineno} {trace_call_result_new.code_line} ")
                print(interpretable_current.interpretable_type)

                from joseph_library.print import print_green
                print_green(f"SIZE {interpretable_current.list_trace_call_result}")

                ###### ENDING STUFF FOR INTERPRETABLES

                # Need to add the new trace
                self.list_trace_call_result.append(trace_call_result_new)

            elif self_from_frame_locals is self:

                _comamnd: Union[PythonCodeAnalyzer.Command, None] = self._list_command.pop() if self._list_command else None

                if _comamnd == PythonCodeAnalyzer.Command.ADD_DICT_FOR_INTERPRETABLE_NEXT:

                    self.list_interpretable.pop()

                    _interpretable_popped = scope_current.pop_interpretable()

                    _dict_k_variable_v_value = _interpretable_popped.get_dict_k_variable_v_value()

                    self.list_dict_k_variable_v_value_for_trace_call_result_next.append(_dict_k_variable_v_value)

                elif _comamnd == PythonCodeAnalyzer.Command.ADD_DICT_FOR_INTERPRETABLE_PREVIOUS:

                    self.list_interpretable.pop()

                    # Event Line Interpretable that is record_dict_for_interpretable_previous()
                    # May have a dict_k_variable_v_value that is from record_dict_for_interpretable_next()
                    _interpretable_popped = scope_current.pop_interpretable()

                    _dict_k_variable_v_value = _interpretable_popped.get_dict_k_variable_v_value()

                    self.list_dict_k_variable_v_value_for_trace_call_result_next.append(_dict_k_variable_v_value)

                    # Actual previous interpretable
                    _interpretable_top = scope_current.get_interpretable_top()

                    _dict_k_variable_v_value = _interpretable_top.get_dict_k_variable_v_value()

                    _interpretable_top.update_dict_k_variable_v_value_through_list(
                        self.list_dict_k_variable_v_value_for_trace_call_result_pervious
                    )


            ##########
            # ENDING STUFF
            ##########

            if event == constants.Event.RETURN.value:

                # IF SELF
                if self_from_frame_locals is self:
                    self.__scope_level_self -= 1

            elif event == constants.Event.CALL.value:

                # IF SELF
                if self_from_frame_locals is self:
                    self.__scope_level_self += 1

            ############
            # ENDING CALLS HERE
            ###########

            print(f"SELF COUNTER: {self.__scope_level_self}")
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
        return len(self.list_stack_scope)

    def record_dict_for_interpretable_next(self, dict_k_variable_v_value: Dict[str, Any]) -> None:
        """
        Update update_dict_k_variable_v_value for interpretable_current by appending the
        dict to a list that will then be exhausted into the next trace_call_result

        :param dict_k_variable_v_value:
        :return:
        """
        self.list_dict_k_variable_v_value_for_trace_call_result_next.append(dict_k_variable_v_value)

        self._list_command.append(PythonCodeAnalyzer.Command.ADD_DICT_FOR_INTERPRETABLE_NEXT)


    def record_dict_for_interpretable_previous(self, dict_k_variable_v_value: Dict[str, Any]) -> None:
        """
        Update update_dict_k_variable_v_value for trace_call_result_previous

        :param dict_k_variable_v_value:
        :return:
        """

        # interpretable_current: Union[Interpretable, None] = (
        #     self.list_interpretable[-1] if self.list_interpretable else None
        # )
        # print("PREEEEE")
        # if interpretable_current is not None:
        #     interpretable_current.update_dict_k_variable_v_value(dict_k_variable_v_value)
        #     print("WHO THE FUCK IS YOU")
        # print("POSSSSSST")

        self.list_dict_k_variable_v_value_for_trace_call_result_pervious.append(dict_k_variable_v_value)

        self._list_command.append(PythonCodeAnalyzer.Command.ADD_DICT_FOR_INTERPRETABLE_PREVIOUS)

        # if self.list_stack_scope:
        #     trace_call_result_previous_by_scope = self.list_stack_scope[-1].get_interpretable_top()
        #
        #     if trace_call_result_previous_by_scope is not None:
        #         from joseph_library.print import print_cyan, print_blue
        #         print("FUJA")
        #         print_cyan(trace_call_result_previous_by_scope)
        #         print_blue(dict_k_variable_v_value)
        #         print("FUJB")
        #         trace_call_result_previous_by_scope.update_dict_k_variable_v_value(dict_k_variable_v_value)

        # for trace_call_result in reversed(self.list_interpretable):
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
        # if self.list_interpretable:
        #     self.list_interpretable[-1].update_dict_k_variable_v_value(dict_k_variable_v_value)

    def print(self):
        print("#" * 100)
        for interpretable in self.list_interpretable:
            print(interpretable)

            print()
