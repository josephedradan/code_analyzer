"""
Created by Joseph Edradan
Github: https://github.com/josephedradan

Date created: 5/21/2022

Purpose:

Details:

Description:

Notes:
    Abusing settrace

    Note that The order of a line of code that is a callable by the trace function is
        Event Line
        Event Call
        Event (whatever it is) THEN Actual code execution of what was for the Event Call was

    Note that for EVERY Event "call" there will always be a corresponding Event "return"
    this allows you to keep track of stack depth

    Trace function
        Notes:
            Arguments (in order) that the a trace function must have
                frame:
                    is the current stack frame

                event:
                    can be:
                    'call', 'line', 'return', 'exception' or 'opcode'

                arg:
                    depends on the event type

        Reference:
            https://docs.python.org/3/library/sys.html

IMPORTANT NOTES:
    YOU CANNOT USE THE DEBUGGER ON THIS APPLICATION BECAUSE IT HIJACKS THE trace function

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
from collections import defaultdict
from enum import Enum, auto
from types import TracebackType, FrameType
from typing import Union, List, Dict, Any

import colorama
import pandas as pd
from code_analyzer import constants
from code_analyzer.interpretable import Interpretable
from code_analyzer.scope import Scope
from code_analyzer.trace_call_result import TraceCallResult

PRINT_FORMAT = "{:<16}{:<10}{:<14}{:<14}{:<16}{} {}"


class CodeAnalyzer:
    class _Procedure(Enum):
        """
        Special procedures that should only be accessed by this object.

        """
        STOP = auto()
        ADD_DICT_FOR_INTERPRETABLE_NEXT = auto()
        ADD_DICT_FOR_INTERPRETABLE_PREVIOUS = auto()

    def __init__(self):
        """
        """

        ##################################################
        """
        Internal Variables
        
        Notes:
            These variables are special and should not be used or seen outside this object
        """

        """
        Scope depth based on if a Event call had this object as its first parameter (This is used to not trace
        code that this object calls because it's not supposed to 
        """
        self.__depth_scope_count_self: int = 0

        # Determine if the code analyzer is _running
        self._running = False

        ####################

        # List of dicts that will be added to the next interpretable
        self._list_dict_k_variable_v_value_for_trace_call_result_next: List[Dict[str, Any]] = []

        # List of dicts that will be added to the previous interpretable
        self._list_dict_k_variable_v_value_for_trace_call_result_previous: List[Dict[str, Any]] = []

        ####################

        # Old trace function (This will most likely be restored)
        self._trace_function_old: Union[TracebackType, None] = None

        ####################

        # List of custom commands that this object uses to do specific actions
        self._list_procedure: List[CodeAnalyzer._Procedure] = []

        ####################

        """
        Very unique condition when a record_dict_for_line from this object was the previous TraceCallResult object made.
        This variable should be handled when the last line of a callable is a:
            code_analyzer.record_dict_for_line_next(...)
            code_analyzer.record_dict_for_line_previous(...)
        This variable handles the TraceCallResult having an Event == Return and is one the of above functions
        """
        self._bool_record_dict_for_line_call_is_trace_call_result_previous = False

        ##################################################
        """
        Varying Internal variables     
        
        Notes:
            You can access them directly if you like, but don't do some crazy modifications to these variables unless
            you know what you are doing.   
        """

        ##
        # TraceCallResult stuff

        self.list_trace_call_result: List[TraceCallResult] = []

        ##
        # Interpretable stuff

        self.list_interpretable: List[Interpretable] = []

        self.interpretable_current: Union[Interpretable, None] = None

        ##
        # Scope stuff

        self.list_stack_scope: List[Scope] = []

        #####
        # Initial scope_parent stuff

        scope_container_initial: Scope = Scope()

        self.list_stack_scope.append(scope_container_initial)

        ##################################################
        """
        Special case Internal variables
        
        Notes:
            These variables are temporary, they will change over time and shouldn't be touched unless you know what you
            are doing
        
        """

        ##
        # INTERPRETABLE CLASS VARIABLES
        self._trace_call_result_possible_on_board_event_line_for_class: Union[TraceCallResult, None] = None

        self._trace_call_result_possible_on_board_event_call_for_class: Union[TraceCallResult, None] = None

        ##################################################
        """
        Analysis variables
        
        Notes:
            These variables are related to analysing the code
        """

        self.dict_k_interpretable_v_list_interpretable: Dict[Interpretable, list] = defaultdict(list)

    def start(self):
        """
        Replace the trace function with a custom trace function that records the lines of python code that can be
        interpreted

        :return:
        """
        self._running = True

        def trace_function_callback(frame: FrameType, event: str, arg):
            """
            Custom trace function

            :param frame:
            :param event:
            :param arg:
            :return:
            """

            nonlocal self

            # filename_full: str = frame.f_code.co_filename

            # TODO LOOK AT THIS
            # if filename_full.startswith('<'):return

            # TODO LOOK AT THIS
            # if not filename_full.is_relative_to(base_dir := Path()):return

            """
            Getting the self variable to indicate if the trace function has caught a callable from this object.
            If the self variable refers to this object, then special procedures will occur.
            
            Notes:
                There can only be one self in the local scope_parent
            """
            self_from_frame_locals: Union[CodeAnalyzer, None] = frame.f_locals.get("self")

            # Current Scope
            scope_current: Scope = self.list_stack_scope[-1]

            # Current interpretable
            interpretable_current: Union[Interpretable, None] = (
                self.list_interpretable[-1] if self.list_interpretable else None
            )

            # Previously made TraceCallResult object
            trace_call_result_previous: Union[TraceCallResult, None] = (
                self.list_trace_call_result[-1] if self.list_trace_call_result else None
            )

            __bool_event_return_and_record_dict_for_line_call_is_trace_call_result_previous = False

            ####################
            # DEBUGGING HEAD START
            ####################A

            # print("-" * 10)
            # print("scope_current:", scope_current)
            # print("interpretable_current:", interpretable_current)
            # print("frame:", frame)
            # print("frame.locals:", frame.f_locals)
            # print("event:", event)
            # print("self:", self_from_frame_locals)
            # print("self.__depth_scope_count_self:", self.__depth_scope_count_self)
            # _trace_call_result_new = TraceCallResult(frame, event, arg, )
            # print("trace_call_result_new (MAY OR MAY NOT EXIST):\n\t{} {} {}".format(
            #     _trace_call_result_new.code_line_strip,
            #     "|||",
            #     _trace_call_result_new.event)
            # )
            # print("trace_call_result_previous:\n\t{}".format(trace_call_result_previous))

            ####################
            # DEBUGGING HEAD END
            ####################

            """
            Analyze the code from the result of this trace function's call
            
            Notes:
                Everything inside of this if statement relates to the code that should be analyzed
            
            """
            if self_from_frame_locals is not self and self.__depth_scope_count_self == 0:

                indent_depth_by_scope = len(self.list_stack_scope)

                ####################
                # SCOPE STUFF (Creating the scope_parent, etc...)
                ####################
                if event == constants.Event.CALL.value:

                    # When a scope_parent is created, the initial level should be 1
                    indent_depth_start = 1

                    # Recall that trace_call_result_previous is the previous interpretable
                    if trace_call_result_previous is not None:
                        indent_depth_start += trace_call_result_previous.get_indent_level_corrected()

                    # Create new Scope
                    scope_new: Scope = Scope(
                        indent_depth_start,
                        indent_depth_by_scope,
                        scope_current  # Parent Scope object
                    )

                    self.list_stack_scope.append(scope_new)

                ####################
                # TraceCallResult
                ####################

                # Create a TraceCall result
                trace_call_result_new = TraceCallResult(
                    frame,
                    event,
                    arg,
                )

                ####################
                # Interpretable RETURN
                ####################
                if event == constants.Event.RETURN.value:
                    """ 
                    Notes:
                        Order of execution when an implicit or explicit return line is hit:
                            1. TraceCallResult with Event == Line Relative to the inner scope_parent
                            2. TraceCallResult with Event == Return Relative to the inner scope_parent
                        
                    """
                    interpretable_current.set_interpretable_type(constants.Event.RETURN)

                    """
                    Special case when a record_dict_for_line is the last call in callable. Look at
                    self._bool_record_dict_for_line_call_is_trace_call_result_previous for more information 
                    """
                    if self._bool_record_dict_for_line_call_is_trace_call_result_previous:
                        __bool_event_return_and_record_dict_for_line_call_is_trace_call_result_previous = True

                    self.list_stack_scope.pop()

                ####################
                # Interpretable CLASS
                ####################
                elif trace_call_result_new.get_python_key_word() == constants.Keyword.CLASS:
                    """
                    Notes:
                        Order of execution when a class defined:
                            1. TraceCallResult with Event == Line Relative to the outer scope_parent
                            2. TraceCallResult with Event == Call Relative to the inner scope_parent
                            3. TraceCallResult with Event == Line Relative to the inner scope_parent
                    
                        For a class to be interpreted correctly, the the below variables must be assigned ot True:
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

                    # Second trace_call_result
                    elif (trace_call_result_new.get_event() == constants.Event.CALL and
                          self._trace_call_result_possible_on_board_event_call_for_class is None):

                        self._trace_call_result_possible_on_board_event_call_for_class = trace_call_result_new

                    # Third trace_call_result
                    elif (self._trace_call_result_possible_on_board_event_line_for_class is not None and
                          self._trace_call_result_possible_on_board_event_call_for_class is not None):

                        self._trace_call_result_possible_on_board_event_line_for_class = None
                        self._trace_call_result_possible_on_board_event_call_for_class = None

                    # IF THE ASSUMPTION FOR CREATING A INTERPRETABLE CLASS WAS INCORRECT, THIS IS THE FALL BACK
                    else:

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
                        Order of execution when the line of code that calls a callable is executed:
                            1. TraceCallResult with Event == Line is created
                            2. TraceCallResult with Event == Call is created
                            3. (In body of callable) TraceCallResult created THEN Execution of that line occurs
                            4. Repeat step 3 until callable ends 
                    
                    """

                    interpretable_current = Interpretable(scope_current, constants.Event.CALL)
                    self.list_interpretable.append(interpretable_current)

                ####################
                # Interpretable (DEFAULT)
                ####################
                else:
                    """
                    Notes:
                        Order of execution when a line of code is None of the prior conditions:
                            1. TraceCallResult with Event == Line is created
                    """

                    interpretable_current = Interpretable(
                        scope_current,
                        constants.Event.LINE)

                    self.list_interpretable.append(interpretable_current)

                ####################
                # Main behavior
                ####################

                """
                Handle special condition regarding a record_dict_for_line call and an Event == Return
                occurring which is to do nothing which means not adding it.
                """
                if __bool_event_return_and_record_dict_for_line_call_is_trace_call_result_previous:

                    """
                    The below will exhaust self._list_dict_k_variable_v_value_for_trace_call_result_next to
                    the current interpretable because any dict_k_variable_v_value_for_trace
                    created from the inner scope does not know anything in the outer scope 
                    
                    """
                    interpretable_current.update_dict_k_variable_v_value_through_exhaustable(
                        self._list_dict_k_variable_v_value_for_trace_call_result_next
                    )

                # Standard behavior
                else:

                    # Exhaust list of dict_k_variable_v_value (The list may be empty)
                    interpretable_current.update_dict_k_variable_v_value_through_exhaustable(
                        self._list_dict_k_variable_v_value_for_trace_call_result_next
                    )

                    # Add the newly created TraceCallResult into interpretable_current
                    interpretable_current.add_trace_call_result(trace_call_result_new)

                    # Correct the scope_parent level of the newly created TraceCallResult
                    if trace_call_result_previous is not None and event == constants.Event.CALL.value:
                        scope_depth_offset = (
                                trace_call_result_previous.get_indent_level_relative_to_scope() -
                                trace_call_result_new.get_indent_level_relative_to_scope()
                        )

                        trace_call_result_new.set_scope_indent_level_offset(scope_depth_offset)

                    # Add the new trace
                    self.list_trace_call_result.append(trace_call_result_new)

                # Resetter
                self._bool_record_dict_for_line_call_is_trace_call_result_previous = False

            ####################
            # self from frame.f_locals is "self" as in "this" object
            ####################
            elif self_from_frame_locals is self:

                # Procedure that must be done if possible
                _procedure: Union[CodeAnalyzer._Procedure, None] = (
                    self._list_procedure.pop() if self._list_procedure else None
                )

                # If the method record_dict_for_line_next() was called
                if _procedure == CodeAnalyzer._Procedure.ADD_DICT_FOR_INTERPRETABLE_NEXT:
                    """
                    Process:
                        1. Pop the previous interpretable that was created from self.list_interpretable 
                            and scope_current.
                            Note that the previous TraceCallResult should have been
                                TraceCallResult with Event == Line
                            and should been a
                                code_analyzer.record_dict_for_line_next()
                            call which is unrelated to the code being analyzed and therefore will be removed
                            (which is why it's popped)
                        2 Route 1. 
                        2 Route 2.  
                    """

                    self.list_interpretable.pop()  # 1.

                    _interpretable_popped = scope_current.pop_interpretable()  # 1.

                    _dict_k_variable_v_value = _interpretable_popped.get_dict_k_variable_v_value()  # 2.
                    if trace_call_result_previous.get_event() == constants.Event.RETURN:
                        # Previous interpretable from the current scope
                        _interpretable_top = scope_current.get_interpretable_top()  # 3.

                        # IF NONE LOOK AT THE PARENT SCOPE FOR THE INTERPRETABLE
                        # 3 Route 1.
                        if _interpretable_top is None:
                            _scope_parent = scope_current.get_scope_parent()

                            # This interpretable should be the top interpretable of the previous scope
                            _interpretable_top = _scope_parent.get_interpretable_top()  # Unlikely to be None

                        # If somehow None...
                        if _interpretable_top is not None:
                            _interpretable_top.update_dict_k_variable_v_value(
                                _dict_k_variable_v_value
                            )

                    else:
                        self._list_dict_k_variable_v_value_for_trace_call_result_next.append(
                            _dict_k_variable_v_value)  # 2.

                    self._bool_record_dict_for_line_call_is_trace_call_result_previous = True

                # If the method record_dict_for_line_previous() was called
                elif _procedure == CodeAnalyzer._Procedure.ADD_DICT_FOR_INTERPRETABLE_PREVIOUS:
                    """
                    Process:
                        1. Pop the previous interpretable that was created from self.list_interpretable 
                            and scope_current/ 
                            Note that the previous TraceCallResult should have been
                                TraceCallResult with Event == Line
                            and should been a
                                code_analyzer.record_dict_for_line_previous()
                            call which is unrelated to the code being analyzed and therefore will be removed
                            (which is why it's popped)
                        2. Steal the popped interpretable's dict_k_variable_v_value and add it to
                            self.list_dict_k_variable_v_value_for_trace_call_result_next
                        3 Route 1A. Get the the most recent interpretable added to the current scope
                            (This is the standard route)
                        3 Route 1B Get the the most recent interpretable added to previous scope if the current scope
                            has no Interpretables
                        3 Route 2. Get the second most recent interpretable added to the current scope
                            because the most recent interpretable is the callable's head e.g. "def function():" 
                            while the second most recent interpretable is the call to that function e.g. "function()"
                            (This route is only taken when the Event == Call)
                        4. Add self._list_dict_k_variable_v_value_for_trace_call_result_previous
                            to that interpretable
                        5. Mark special condition that operation was done
                         
                    """
                    self.list_interpretable.pop()  # 1.

                    """
                    Event Line Interpretable that is record_dict_for_line_previous()
                    May have a dict_k_variable_v_value that is from record_dict_for_line_next()
                    """
                    _interpretable_popped = scope_current.pop_interpretable()  # 1.

                    _dict_k_variable_v_value = _interpretable_popped.get_dict_k_variable_v_value()  # 2.

                    self._list_dict_k_variable_v_value_for_trace_call_result_next.append(_dict_k_variable_v_value)  # 2.

                    # Previous interpretable from the current scope
                    _interpretable_top = scope_current.get_interpretable_top()  # 3.

                    # 3 Route 1B. No top Interpretable -> get parent scope's top Interpretable
                    if _interpretable_top is None:
                        _scope_parent = scope_current.get_scope_parent()

                        # This interpretable should be the top interpretable of the previous scope
                        _interpretable_top = _scope_parent.get_interpretable_top()

                    # 3 Route 1A. Top Interpretable exists
                    else:

                        # This TraceCallResult may have the Event == Call or not exist at all
                        _trace_call_result_primary: Union[TraceCallResult, None] = (
                            _interpretable_top.get_trace_call_result_primary()
                        )

                        # 3 Route 2. Top Interpretable's primary TraceCallResult has Event == Call
                        if _trace_call_result_primary.get_event() == constants.Event.CALL:
                            """
                            The below will select the correct Interpretable  
                            
                            Example:
                                Code:
                                    do_something()  
                                    code_analyzer.record_dict_for_line_previous({"Key": "Value"})
                                    
                                Result:
                                    do_something()  {"Key": "Value"}
                                    ...                             
                                    
                            """
                            _interpretable_top = scope_current.get_interpretable(-2)

                    # 4.
                    _interpretable_top.update_dict_k_variable_v_value_through_exhaustable(
                        self._list_dict_k_variable_v_value_for_trace_call_result_previous
                    )

                    self._bool_record_dict_for_line_call_is_trace_call_result_previous = True

            ##########
            # Event based specific operations
            ##########
            if event == constants.Event.RETURN.value:

                if self_from_frame_locals is self:
                    self.__depth_scope_count_self -= 1

            elif event == constants.Event.CALL.value:

                if self_from_frame_locals is self:
                    self.__depth_scope_count_self += 1

            ####################
            # DEBUGGING TAIL START
            ####################

            # print(f"SELF COUNTER: {self.__depth_scope_count_self}")
            # print("-" * 10)

            ####################
            # DEBUGGING TAIL END
            ####################

            return trace_function_callback

        sys.settrace(trace_function_callback)

    def stop(self) -> None:

        """
        1. Restores trace function to the original one
        2. Perform any post analysis
        """
        sys.settrace(self._trace_function_old)

        self._do_post_analyze()

        self._running = False

    def _do_post_analyze(self):
        """
        Any post analysis on the code that was analyzed
        :return:
        """

        for index, interpretable in enumerate(self.list_interpretable):
            self.dict_k_interpretable_v_list_interpretable[interpretable].append(interpretable)

            list_interpretable = self.dict_k_interpretable_v_list_interpretable.get(interpretable)

            execution_number_relative = len(list_interpretable)

            interpretable.set_anlaysis_info(execution_number_relative, index)

    def record_dict_for_line_next(self, dict_k_variable_v_value: Dict[str, Any]) -> None:
        """
        Update update_dict_k_variable_v_value for interpretable_current by appending the
        dict to a list that will then be exhausted into the next trace_call_result

        :param dict_k_variable_v_value:
        :return:
        """
        self._list_dict_k_variable_v_value_for_trace_call_result_next.append(dict_k_variable_v_value)

        self._list_procedure.append(CodeAnalyzer._Procedure.ADD_DICT_FOR_INTERPRETABLE_NEXT)

    def record_dict_for_line_previous(self, dict_k_variable_v_value: Dict[str, Any]) -> None:
        """
        Update update_dict_k_variable_v_value for trace_call_result_previous

        :param dict_k_variable_v_value:
        :return:
        """

        self._list_dict_k_variable_v_value_for_trace_call_result_previous.append(dict_k_variable_v_value)

        self._list_procedure.append(CodeAnalyzer._Procedure.ADD_DICT_FOR_INTERPRETABLE_PREVIOUS)

    def print(self):

        if self._running:
            raise Exception("Cannot call this function until the stop method is called!")

        print("{}\n{}\n{}\n".format("#" * 100, "*** CODE ANALYSIS ***", "#" * 100))

        ########################################

        print("{}\n{}\n{}\n".format("-" * 50, "Execution Analysis", "-" * 50))

        colorama.init()

        print(_get_execution_analysis_string("Exe Index Rel", "Line #", "Scope depth", "Indent lvl", "Exe #", "Code + {Variable: Value}",
                                             ""))
        for interpretable in self.list_interpretable:
            print(_get_execution_analysis_string_interpretable(interpretable))

        ########################################

        print("{}\n{}\n{}\n".format("-" * 50, "Line Analysis", "-" * 50))

        list_interpretable: List[Interpretable]
        for interpretable, list_interpretable in self.dict_k_interpretable_v_list_interpretable.items():
            trace_call_result = interpretable.get_trace_call_result_primary()

            line_of_code = trace_call_result.code_line_strip

            filename_full = trace_call_result.filename_full

            count = len(list_interpretable)

            print("\nLine of Code: {}\nFile: {}\nCount: {}".format(line_of_code, filename_full, count))

            generator_information = ((
                _interpretable.execution_index_global,
                _interpretable.execution_number_relative,
                _interpretable.dict_k_variable_v_value
            ) for _interpretable in list_interpretable)

            df_information = pd.DataFrame(
                generator_information,
                columns=["Execution Index",
                         "Scope Depth"
                         "Execution Number Relative",
                         "{Key: Value} Pairs"])

            with pd.option_context('display.max_rows', None, ):
                print(df_information.to_string())

            print("\n-----")


def _get_execution_analysis_string_interpretable(interpretable: Interpretable):
    trace_call_result = interpretable.get_trace_call_result_primary()

    #####

    line_number = trace_call_result.code_line_number

    indent_depth_by_scope = interpretable.scope_parent.indent_depth_by_scope

    indent_level = trace_call_result.get_indent_level_corrected()

    code = str(trace_call_result)

    #####

    dict_k_variable_v_value = interpretable.get_dict_k_variable_v_value()
    dict_k_variable_v_value = dict_k_variable_v_value if dict_k_variable_v_value else ""

    ##########

    return _get_execution_analysis_string(
        interpretable.get_execution_index_global(),
        line_number,
        indent_depth_by_scope,
        indent_level,
        interpretable.get_execution_number_relative(),
        code,
        dict_k_variable_v_value
    )


def _get_execution_analysis_string(execution_index,
                                   line_number,
                                   depth_scope,
                                   indent_level,
                                   execution_number_relative,
                                   code,
                                   dict_k_variable_v_value
                                   ):
    string = PRINT_FORMAT.format(
        execution_index,
        line_number,
        depth_scope,
        indent_level,
        execution_number_relative,
        code,
        colorama.Fore.RED + str(dict_k_variable_v_value) + colorama.Style.RESET_ALL
    )

    return string
