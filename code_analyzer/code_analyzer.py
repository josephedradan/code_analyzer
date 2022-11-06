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

                str_event:
                    can be:
                    'call', 'line', 'return', 'exception' or 'opcode'

                arg:
                    depends on the str_event type

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

    So You Wanna Be a Pandas Expert? (Tutorial) - James Powell | PyData Global 2021
        Notes:
            What my code is based on
        Reference:
            https://youtu.be/pjq3QOxl9Ok?t=2720
"""
import sys
from collections import defaultdict
from enum import Enum, auto
from functools import wraps
from types import TracebackType, FrameType
from typing import Union, List, Dict, Any, Callable

from code_analyzer import constants
from code_analyzer.code_analyzer_printer import CodeAnalyzerPrinter
from code_analyzer.exception import NoScopeAvailable, IllegalCall
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

        """
        Original trace function that is past the scope containing the called start() method 
        (This will most likely be restored)
        
        """
        self._trace_function_original: Union[TracebackType, None] = None

        """
        Original trace function in the scope where the start() method is called (This will most likely be restored)
        
        Notes:
            Note that the location of this trace function is located where the start() method is located 
        
        """
        self._trace_function_original_base: Union[TracebackType, None] = None

        ####################

        # List of custom commands that this object uses to do specific actions
        self._list_procedure: List[CodeAnalyzer._Procedure] = []

        ####################

        """
        Very unique condition when one of the below code lines
            .record_dict_for_line_next(...)
            OR
            .record_dict_for_line_previous(...)
        has their frame's str_event == constants.Event.RETURN.value  
        
        This basically means that one of the above code lines was the last line of a callable        
        """
        self._bool_record_dict_for_line_call_is_trace_call_result_previous = False

        ##################################################
        """
        Varying Internal variables     
        
        Notes:
            You can access them directly if you like, but don't do some crazy modifications to these variables unless
            you know what you are doing.   
        """

        ####################
        # Interpretable stuff
        ####################
        self.list_interpretable: List[Interpretable] = []

        ####################
        # Code Analyzer Printer
        ####################

        self.code_analyzer_printer: CodeAnalyzerPrinter = CodeAnalyzerPrinter(self)

        ##################################################

        """
        Special case Internal variables
        
        Notes:
            These variables are temporary, they will change over time and shouldn't be touched unless you know what you
            are doing
        
        """

        ####################
        # TraceCallResult stuff
        ####################

        # All TraceCallResult objects (This shouldn't be used for anything important)
        self._list_trace_call_result_raw: List[TraceCallResult] = []

        ####################
        # Interpretable stuff
        ####################

        self._interpretable_current: Union[Interpretable, None] = None

        ####################
        # Scope stuff
        ####################

        self._list_stack_scope: List[Scope] = []

        # Initial scope_parent stuff
        scope_container_initial: Scope = Scope()

        self._list_stack_scope.append(scope_container_initial)

        ####################
        """
        self._index_frame_object is used as a variable in sys._getframe(self._index_frame_object).f_trace
        to get the frame's trace function. That frame's trace function will ten be replace with 
        the trace function trace_function_callback(...) so that code executed from that frame can be analyzed.
        
        If the index is 1, then the code that should be analyzed probably follows the format below:
            code_analyzer = CodeAnalyzer() 
            code_analyzer.start()
            ... # CODE BEING ANALYZED IS HERE
            code_analyzer.stop() 
            code_analyzer.print()
        
        If the index is 2, then the code that should be analyzed probably follows the format below:
            code_analyzer = CodeAnalyzer()
            with code_analyzer as ca:
                ... # CODE BEING ANALYZED IS HERE
            code_analyzer.print()
        
        """
        self._index_frame_object: Union[int, None] = None

        ####################

        # INTERPRETABLE CLASS VARIABLES
        self._trace_call_result_possible_on_board_event_line_for_class: Union[TraceCallResult, None] = None

        self._trace_call_result_possible_on_board_event_call_for_class: Union[TraceCallResult, None] = None

        # If the decorator method of using this application was called
        self._decorator_used: bool = False

        # If the decorator method needs to execute special code
        self._decorator_used_do_conditions: bool = False

        ##################################################
        """
        Analysis variables
        
        Notes:
            These variables are related to analyzing the code
        """

        # This is used to count the amount of times an interpretable has been called
        self.dict_k_interpretable_v_list_interpretable: Dict[Interpretable, list] = defaultdict(list)

    def __enter__(self):
        """
        Notes:
            The value of self._index_frame_object is set to 2 because the index 2 contains the code within the
            "With" keyword scope

            THIS MUST BE CALLED BEFORE self.start()

        :return:
        """
        self._index_frame_object = 2

        self.start()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def __call__(self, callable_: Callable = None):
        """
        Higher order decorator

        :param callable_:
        :return:
        """

        def decorator_actual(callable__: Callable):
            @wraps(callable__)
            def wrapper(*args, **kwargs):
                nonlocal self

                self._decorator_used = True  # Signify that the decorator method was used
                self._decorator_used_do_conditions = True

                self.start()
                result = callable__(*args, **kwargs)
                self.stop()

                return result

            return wrapper

        return decorator_actual(callable_) if callable_ else decorator_actual

    def start(self):
        """
        Replace the trace function with a custom trace function that records the lines of python code that can be
        interpreted

        :return:
        """

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

            if not self._list_stack_scope:
                raise NoScopeAvailable("No scope is available, the possible errors are 1. Is stop() called on in a "
                                       "higher scope, make sure that the stop() method is called in a scope that is "
                                       "on the same level as the start() method or deeper. 2. The analyzer has a"
                                       "a coding error.")

            # Current Scope
            scope_current: Scope = self._list_stack_scope[-1]

            """
            Current interpretable
            
            Notes:
                DO NOT USE scope_current.get_interpretable(), self.list_interpretable allows 
                access to the previous interpretable that may not be relative to the scope_current as it
                might be from the previous scope. An example of this functionality is communicating with
                a function definition from that function's interpretables.
                
            """
            interpretable_current: Union[Interpretable, None] = (
                self.list_interpretable[-1] if self.list_interpretable else None
            )

            # Previously made TraceCallResult object
            trace_call_result_previous: Union[TraceCallResult, None] = (
                self._list_trace_call_result_raw[-1] if self._list_trace_call_result_raw else None
            )

            __bool_event_return_and_record_dict_for_line_call_is_trace_call_result_previous = False

            ####################
            # DEBUGGING HEAD START
            ####################

            print("-" * 10)
            print("scope_current:", scope_current)
            print("scope_current depth:", scope_current.get_indent_depth_scope())
            print("scope_current.get_interpretable()", scope_current.get_interpretable())
            print("interpretable_current:", interpretable_current)
            print("frame:", frame)
            print("frame.locals:", frame.f_locals)
            print("str_event:", event)
            print("self:", self_from_frame_locals)
            print("self.__depth_scope_count_self:", self.__depth_scope_count_self)
            _trace_call_result_new = TraceCallResult(frame, event, arg, )
            print("trace_call_result_new (MAY OR MAY NOT EXIST):\n\t{} {} {}".format(
                _trace_call_result_new.code_line_strip,
                "|||",
                _trace_call_result_new.str_event)
            )
            print("trace_call_result_previous:\n\t{} ||| {}".format(
                trace_call_result_previous,
                trace_call_result_previous.str_event if trace_call_result_previous else "")
            )

            ####################
            # DEBUGGING HEAD END
            ####################

            """
            Analyze the code from the result of this trace function's call
            
            Notes:
                Everything inside of this if statement relates to the code that should be analyzed
            
            """
            if self_from_frame_locals is not self and self.__depth_scope_count_self == 0:

                """
                ####################
                # Creating a future scope
                ####################
                
                IMPORTANT NOTES:
                    THE CODE BELOW MUST BE PLACED HERE BECAUSE THERE ARE 2 PLACES WHERE
                    A CONDITION USING constants.Event.CALL IS USED WHICH WOULD MAKE THE CODE BELOW APPLY
                    TO THOSE PLACES
                
                """
                if event == constants.Event.CALL.value:
                    # When a scope_parent is created, the initial level should be 1
                    indent_depth_offset = 0

                    # Recall that trace_call_result_previous is the previous interpretable
                    if trace_call_result_previous is not None:
                        indent_depth_offset += trace_call_result_previous.get_indent_depth_relative()

                    # Create new Scope
                    scope_new: Scope = Scope(
                        scope_current,  # Parent Scope object
                        indent_depth_offset
                    )

                    """
                    If the decorator method of running this application was used (Part 1)
                    
                    Notes:
                        The body of the condition below prevents the creation of a new Scope because that scope is not 
                        related to the code being analyzed because it's the decorator scope. Also, a scope still needs 
                        to be added to self._list_stack_scope to prevent this application from raising an exception
                        relating to popping from an empty list. To prevent the exception, scope_current is re added 
                        to the list as a cheap trick to prevent the exception.
                        
                    """
                    if self._decorator_used_do_conditions is True:
                        scope_new = scope_current

                    self._list_stack_scope.append(scope_new)

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
                if trace_call_result_new.get_event() == constants.Event.RETURN:  # TODO: CHECK trace_call_result_new.get_event() instead of str_event .also constants.Event.RETURN.value
                    """ 
                    
                    Notes:
                        Order of execution when an implicit or explicit return line is hit:
                            1. TraceCallResult with Event == LINE, Keyword == return, and
                                Relative to the inner scope_parent
                            2. TraceCallResult with Event == RETURN, Keyword == return, and
                                Relative to the inner scope_parent
                        
                    """

                    #######

                    # By Scope because validation of correct scope
                    _interpretable_current_by_scope = scope_current.get_interpretable_top()

                    """
                    
                    Notes:
                        If scope_current has no interpretables then whatever cause the creation of the scope
                        has nothing inside of it which is not possible in python. The only possible way for
                        a scope to be empty in this case must have been from one of this object's methods being
                        called such as from a .record_dict_for_line_previous(...) call.
                    
                    """
                    if _interpretable_current_by_scope:

                        """
                        Notes:
                            if condition:
                                Assumes that both the current Interpretable (from self.list_interpretable)
                                and the top Interpretable (from the current scope) are the same.
                                
                                Assumes that the previously made TraceCallResult has a return.
                                
                                Recall that all functions have a return regardless of the code being analyzed
                                has one written or not. 
                                 
                                Basically the code handles if an actual return was written or a
                                not real return (fake return) was made and will assign the correct event for that
                                Interpretable.
                                
                                Example:
                                    Code:
                                        def get(x):
                                            x  # Will cause an fake return, does not actually return x
                                        get(1)
                                        
                                    TraceCallResults in raw form (Exactly what TraceCallResult objects are made):
                                        def get(x):
                                        get(1) | Line
                                        def get(x): | Call
                                            x | Line
                                            x | Return  # This return will make the previous TraceCallResult a return
                                    
                                In the example above, the final return will have an Event == RETURN, but it shouldn't
                                because the original code did not have a actual return written in the get function
                            
                            else condition:
                                Assumes that both the current Interpretable (from self.list_interpretable)
                                and the top Interpretable (from the current scope) are in different scopes.
                                Following the above statement, due to trace_call_result_new having its Event == RETURN,
                                interpretable_current must be an actual or fake return.
                                
                                Basically, if 2 returns are made sequentially then both TraceCallResults will be in the 
                                same interpretable which makes no sense because the second TraceCallResult is in a 
                                higher scope. So the code in this condition will move the second TraceCallResult
                                to its correct Interpretable which should have Event == LINE. This code also assigns the
                                correct Event to the Interpretable that received the second TraceCallResult 
                                
                                Note that _interpretable_current_by_scope at this point should be the Interpretable
                                for the function call with Event == CALL
                                    Example:
                                        ...
                                        a = func()
                                        def func():  # <- This is the Interpretable with Event == CALL 
                                            ...
                                Note that interpretable_current at this point should be replaced with the Interpretable
                                before the Interpretable listed above
                                    Example:
                                        ...
                                        a = func()  # <- This Interpretable
                                        def func():  
                                            ...
                                
                                Example:
                                    Code:
                                        def main():
                                            def example():
                                                def get(x):
                                                    return x
                                                return get(1)
                                            example()
                                        main():
                                        
                                    TraceCallResults in raw form (Exactly what TraceCallResult objects are made):
                                        def main():
                                        main()
                                        def main():
                                            def example(): | LINE
                                            example() | LINE  # Should not be a Return (Line is correct)
                                            def example(): | CALL
                                                def get(x): | LINE
                                                return get(1) | Line  # Should be a Return
                                                def get(x): | CALL
                                                    return x | LINE
                                                    return x | RETURN
                                            return example() | RETURN  # Should be in the Interpretable "example() | Line"
                                        
                                    In the example, 2 correction should be made:
                                        The Interpretable containing "example() | LINE" should contain 
                                        TraceCallResult "return example() | RETURN" and that Interpretable should
                                        keep its Event == LINE because the the function example() does not return
                                        anything which also means that "example() | LINE" will be the primary
                                        TraceCallResult
                                        
                                        Interpretable for "return get(1) | Line" should contain TraceCallResult 
                                        "return x | Return" and the Interpretable should have its Event == RETURN.
                                        This also means that the primary TraceCallResult will be "return x | Return"
                                
                                Example 2 (class):
                                    Code:
                                        def func(): 
                                            class Josh:
                                                def __init__(self):
                                                    pass
                                                pass 
                                                
                                    TraceCallResults in raw form (Exactly what TraceCallResult objects are made):
                                        def func(): | LINE
                                        func() | LINE
                                        def func(): | CALL
                                            class Josh: | LINE
                                            class Josh: | CALL
                                            class Josh: | LINE
                                                def __init__(self): | LINE
                                                pass | LINE
                                                pass | RETURN
                                            class Josh: | RETURN  # This should be moved

                                    In this example, THe TraceCallResult "class Josh: | RETURN" should in the 
                                    Interpretable containing "class Josh: | LINE"

                        """

                        # Check if both Interpretables are itself (Implies that the scope is the same)
                        if interpretable_current == _interpretable_current_by_scope:

                            if trace_call_result_previous.get_python_key_word() == constants.Keyword.RETURN:
                                interpretable_current.set_interpretable_type(constants.Event.RETURN)

                        else:

                            _interpretable_current_by_scope = scope_current.get_interpretable_top()

                            # Special cass if _interpretable_current_by_scope's type is a class
                            if _interpretable_current_by_scope.get_interpretable_type() == constants.Keyword.CLASS:

                                interpretable_current = _interpretable_current_by_scope

                            else:  # Standard behavior

                                # Should be the Interpretable right before the function call
                                _interpretable_current_by_scope = scope_current.get_interpretable(-2)

                                interpretable_current = _interpretable_current_by_scope

                            _trace_call_result_line = interpretable_current.get_trace_call_result_primary()

                            if _trace_call_result_line.get_python_key_word() == constants.Keyword.RETURN:
                                interpretable_current.set_interpretable_type(constants.Event.RETURN)

                    """
                    Special case when a record_dict_for_line is the last call in callable. Look at
                    self._bool_record_dict_for_line_call_is_trace_call_result_previous for more information 
                    """
                    if self._bool_record_dict_for_line_call_is_trace_call_result_previous:
                        __bool_event_return_and_record_dict_for_line_call_is_trace_call_result_previous = True

                    self._list_stack_scope.pop()

                ####################
                # Interpretable CLASS
                ####################
                elif trace_call_result_new.get_python_key_word() == constants.Keyword.CLASS:
                    """
                    Notes:
                        Note that the 3 TraceCallResult objects past this point all start with the python
                        keyword class 
                        
                        Order of execution when a class defined:
                            1. TraceCallResult with Event == LINE Relative to the outer scope_parent
                            2. TraceCallResult with Event == CALL Relative to the inner scope_parent
                            3. TraceCallResult with Event == LINE Relative to the inner scope_parent
                    
                        For a class to be interpreted correctly, the the below variables must be assigned ot True:
                            _trace_call_result_possible_on_board_event_line_for_class
                            _trace_call_result_possible_on_board_event_call_for_class
                    """

                    # First trace_call_result
                    if (trace_call_result_new.get_event() == constants.Event.LINE and
                            self._trace_call_result_possible_on_board_event_line_for_class is None):

                        # Replace _interpretable_current with a new one
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
                elif trace_call_result_new.get_event() == constants.Event.CALL:  # Notice that the value of the Enum is compared # TODO: CHECK trace_call_result_new.get_event() instead of str_event
                    """
                    
                    Notes:
                        Order of execution when the line of code that calls a callable is executed:
                            1. TraceCallResult with Event == LINE is created
                            2. TraceCallResult with Event == CALL is created
                            3. (In body of callable) TraceCallResult created THEN Execution of that line occurs
                            4. Repeat step 3 until callable ends 
                    
                    """

                    interpretable_current = Interpretable(scope_current, constants.Event.CALL)

                    """
                    If the decorator method of running this application was used (Part 2)
                    
                    IMPORTANT NOTES:
                        RECALL THAT AN INTERPRETABLE MUST EXIST PAST THIS CONDITION
                        
                    Notes:
                        Recall that the scope given to creating a interpretable automatically
                        adds the interpretable to that scope. 
                        
                        Recall that the interpretable created if the condition below is met, is the 
                        decorator interpretable which must be removed because it's unrelated to the code being 
                        analyzed.
                        
                        The below will remove the decorator interpretable from the current scope and
                        not add the interpretable to this object's list of interpretables.
                    
                    """
                    if self._decorator_used_do_conditions is True:
                        scope_current.pop_interpretable()  # Note: If you don't print this, then code will work
                    else:
                        self.list_interpretable.append(interpretable_current)

                ####################
                # Interpretable (DEFAULT)  # New interpretable
                ####################
                else:
                    """
                    Notes:
                        Order of execution when a line of code is None of the prior conditions:
                            1. TraceCallResult with Event == LINE is created
                    """

                    interpretable_current = Interpretable(
                        scope_current,
                        constants.Event.LINE)

                    self.list_interpretable.append(interpretable_current)

                """
                ####################
                # Main behavior
                ####################
                
                IMPORTANT NOTES:
                    At this point 
                        _interpretable_current MUST exist
                        trace_call_result_new MUST exist
                """

                """
                Handle special condition regarding the line of code below
                    .record_dict_for_line_previous(...)
                is the trace_call_result_new. Basically, don't add trace_call_result_new to the 
                _interpretable_current because it has nothing to do with the code being analyzed.
                """
                if __bool_event_return_and_record_dict_for_line_call_is_trace_call_result_previous:
                    """
                    The below will exhaust self._list_dict_k_variable_v_value_for_trace_call_result_next to
                    the current interpretable because the current str_event is a return so no new Tnterpretables 
                    and therefore TraceCallResult objects will be made past this point.
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

                    # Add the newly created TraceCallResult into _interpretable_current
                    interpretable_current.add_trace_call_result(trace_call_result_new)

                    """
                    Correct the indent depth for the newly created TraceCallResult
                    
                    Notes:
                        Primarily used for correcting function calls to be in their correct scope
                        regardless from where they were defined. For example, if a function is defined on
                        indent depth 20 and that function is called on indent depth 10, then the analyzer
                        will move the function call and its body to the correct indent depth of 10 which
                        represents the correct scope where the code is being interpreted at.
                        
                    """
                    if trace_call_result_previous is not None and event == constants.Event.CALL.value:
                        indent_depth_offset = (
                                trace_call_result_previous.get_indent_depth_relative_to_scope() -
                                trace_call_result_new.get_indent_depth_relative_to_scope()
                        )

                        trace_call_result_new.set_indent_depth_offset(indent_depth_offset)

                    # Add the new trace
                    self._list_trace_call_result_raw.append(trace_call_result_new)

                    """
                    If the decorator method of running this application was used (Part 3)
                    
                    Notes:
                        
                    
                    """
                    if self._decorator_used_do_conditions is True:
                        self._list_trace_call_result_raw.pop()
                        self._decorator_used_do_conditions = False

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
                                TraceCallResult with Event == LINE
                            and should been a
                                code_analyzer.record_dict_for_line_next()
                            call which is unrelated to the code being analyzed and therefore will be removed
                            (which is why it's popped)
                        2. Get the dict of the variable and its value
                        3A. If the previous trace_call_result_previous's str_event was a constants.Event.RETURN
                            (It's probably not possible to get in this route because of )
                        3A1. Get the top interpretable in the current scope
                        3A2. If the top interpretable of the current scope does not exist, then get the parent scope's
                            top interpretable instead
                        3B. (Standard behavior) Add _dict_k_variable_v_value to update the next interpretable 
                    """

                    self.list_interpretable.pop()  # 1.

                    _interpretable_popped = scope_current.pop_interpretable()  # 1.

                    _dict_k_variable_v_value = _interpretable_popped.get_dict_k_variable_v_value()  # 2.

                    if trace_call_result_previous.get_event() == constants.Event.RETURN:  # 3A

                        # Previous interpretable from the current scope
                        _interpretable_top = scope_current.get_interpretable_top()

                        # 3A1. IF NONE LOOK AT THE PARENT SCOPE FOR THE INTERPRETABLE
                        if _interpretable_top is None:
                            _scope_parent = scope_current.get_scope_parent()

                            # This interpretable should be the top interpretable of the previous scope
                            _interpretable_top = _scope_parent.get_interpretable_top()  # Unlikely to be None

                        # 3A2. If the top interpretable exist by now, update its dict
                        if _interpretable_top is not None:
                            _interpretable_top.update_dict_k_variable_v_value(
                                _dict_k_variable_v_value
                            )

                    # 3B. Standard behavior
                    else:
                        self._list_dict_k_variable_v_value_for_trace_call_result_next.append(
                            _dict_k_variable_v_value)

                    # self._bool_record_dict_for_line_call_is_trace_call_result_previous = True  # Why is this here?

                # If the method record_dict_for_line_previous() was called
                elif _procedure == CodeAnalyzer._Procedure.ADD_DICT_FOR_INTERPRETABLE_PREVIOUS:
                    """
                    Process:
                        1. Pop the previous Interpretable that was created from self.list_interpretable 
                            and scope_current
                            Note that the previous TraceCallResult should have been
                                TraceCallResult with Event == LINE
                            and should been a
                                .record_dict_for_line_previous(...)
                            call which is unrelated to the code being analyzed and therefore will be removed
                            (which is why it's popped)
                        2. Steal the popped Interpretable's dict_k_variable_v_value and add it to
                            self.list_dict_k_variable_v_value_for_trace_call_result_next because
                            this Interpretable is popped and so that dict needs to be moved to the next
                            Interpretable 
                        3A. Get the the most recent interpretable added to the current scope
                            (This is the standard route)
                        3A1. Get the second most recent interpretable added to the current scope
                            because the most recent interpretable is the callable's head e.g. "def function():" 
                            while the second most recent interpretable is the call to that function e.g. "function()"
                            (This route is only taken when the Event == CALL)
                        3B. Get the the most recent interpretable added to previous scope if the current scope
                            has no Interpretables
                        3B1. If parent scope exists, then use its top Interpretable otherwise move 
                            self._list_dict_k_variable_v_value_for_trace_call_result_previous into
                            self._list_dict_k_variable_v_value_for_trace_call_result_next because
                            self._list_dict_k_variable_v_value_for_trace_call_result_previous will have
                            nowhere else to be added 
                            
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

                    self._list_dict_k_variable_v_value_for_trace_call_result_next.append(
                        _dict_k_variable_v_value)  # 2.

                    # Previous interpretable from the current scope
                    _interpretable_top = scope_current.get_interpretable_top()  # 3.

                    # 3B. No top Interpretable -> use parent scope's top Interpretable if possible
                    if _interpretable_top is None:
                        _scope_parent = scope_current.get_scope_parent()

                        # 3B1. If there is a parent scope
                        if _scope_parent:
                            # This interpretable should be the top interpretable of the previous scope
                            _interpretable_top = _scope_parent.get_interpretable_top()
                        else:
                            self._list_dict_k_variable_v_value_for_trace_call_result_next.extend(
                                self._list_dict_k_variable_v_value_for_trace_call_result_previous
                            )

                            self._list_dict_k_variable_v_value_for_trace_call_result_previous.clear()

                    # 3A. Top Interpretable exists
                    else:

                        # This TraceCallResult may have the Event == CALL or not exist at all
                        _trace_call_result_primary: Union[TraceCallResult, None] = (
                            _interpretable_top.get_trace_call_result_primary()
                        )

                        # 3A1. Top Interpretable's primary TraceCallResult has Event == CALL
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
                    if _interpretable_top:
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

        ########################################

        # Set the default self._index_frame_object
        if self._index_frame_object is None:
            self._index_frame_object = 1

        self._trace_function_original = sys.gettrace()
        self._trace_function_original_base = sys._getframe(self._index_frame_object).f_trace

        self._running = True

        # Replacing the current trace functions
        sys._getframe(self._index_frame_object).f_trace = trace_function_callback
        sys.settrace(trace_function_callback)

    def stop(self) -> None:
        """
        1. Restores trace function to the original one
        2. Perform any post analysis
        3. Reset
        """

        if self._running:  # This guard prevents potential exceptions and bugs from occurring

            # Restoring the current trace functions to its original function
            sys._getframe(self._index_frame_object).f_trace = self._trace_function_original_base
            sys.settrace(self._trace_function_original)

            ##########

            """
            Checking to drop the last Interpretable object in self.list_interpretable because
            the last interpretable is unrelated to the code being tested, the last interpretable is probably
            a .stop() method call
            
            Notes:
                Condition:
                    self._index_frame_object == 1  
                        Recall
                            self._index_frame_object == 1 
                                Probably means that the methods .start() and .stop() were used to analyze code
                                
                            self._index_frame_object == 2 
                                Probably means that the "with" keyword was used.
                                
                    indent_depth_scope > 0
                        When indent_depth_scope is > 0 a stop() calls from a deeper scope relative to the start() 
                        method was called.
                         
            IMPORTANT NOTES:
                COMMENT OUT THE CODE BELOW FOR DEBUGGING
            """
            if self.list_interpretable:
                interpretable_last: Interpretable = self.list_interpretable[-1]

                # indent_depth_scope = interpretable_last.get_scope_parent().get_indent_depth_scope()
                indent_depth_scope = self._list_stack_scope[-1].get_indent_depth_scope()  # TODO: DO CRASH PROTECTION
                """
                Possible Conditions:
                    1. When self._index_frame_object == 1, a .stop() call will be the last
                    interpretable which needs to be removed because it is not related to code being analyzed
                    
                    2. When self._index_frame_object == 2, nothing happens because it doesn't have the same
                    problems when self._index_frame_object == 1
                    
                    3. When indent_depth_scope > 0, a deeper level .stop() call was called and that .stop()
                    interpretable must be removed
                    
                    4. When self._decorator_used is False and self._index_frame_object == 1
                    the decorator method of running this code was used so the .stop() is on a higher or equal scope 
                    depth relative to the .start() call. However due to the decorator forcing all the code being a
                    analyzed to be in a 1 level deeper scope depth, a return line will be added and will need to
                    be removed.
                    
                """

                if (self._index_frame_object == 1 and not self._decorator_used) or indent_depth_scope > 0:

                    # Remove the top interpretable from the last scope
                    _interpretable_top_popped = self.list_interpretable.pop()

                    if self.list_interpretable:  # Might be empty
                        """
                        Due to _interpretable_top_popped being removed because 
                            1. it's not code that should be analyzed.
                            2. it possibly has a dict_k_variable_v_value that it shouldn't have.
                        The dict_k_variable_v_value must be moved to the actual top Interpretable
                        """
                        _interpretable_top_actual: Interpretable = self.list_interpretable[-1]
                        _interpretable_top_actual.update_dict_k_variable_v_value(
                            _interpretable_top_popped.dict_k_variable_v_value
                        )

                    self._decorator_used = False

                if self.list_interpretable:  # Might be empty
                    """
                    If self._list_dict_k_variable_v_value_for_trace_call_result_next has any
                    dict_k_variable_v_values left over, those dict_k_variable_v_values must added to the
                    top interpretable
                    """
                    _interpretable_top: Interpretable = self.list_interpretable[-1]
                    _interpretable_top.update_dict_k_variable_v_value_through_exhaustable(
                        self._list_dict_k_variable_v_value_for_trace_call_result_next
                    )

            ##########

            self._do_post_analyze()

            self._running = False

            self._trace_function_original = None
            self._trace_function_original_base = None

            self._index_frame_object = None

    def _do_post_analyze(self):
        """
        Any post analysis on the code that was analyzed
        :return:
        """

        self.dict_k_interpretable_v_list_interpretable.clear()  # Resetter/Cleaner

        for index, interpretable in enumerate(self.list_interpretable):
            self.dict_k_interpretable_v_list_interpretable[interpretable].append(interpretable)

            list_interpretable = self.dict_k_interpretable_v_list_interpretable.get(interpretable)

            execution_number_relative = len(list_interpretable)

            interpretable.set_anlaysis_info(execution_number_relative, index)

    def record_dict_for_line_next(self, dict_k_variable_v_value: Dict[str, Any]) -> None:
        """
        Update update_dict_k_variable_v_value for _interpretable_current by appending the
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
            raise IllegalCall("Cannot call this function until the stop method is called!")

        self.code_analyzer_printer.print()

    def get_list_interpretable(self) -> List[Interpretable]:
        return self.list_interpretable
