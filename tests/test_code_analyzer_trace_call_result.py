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
from code_analyzer import CodeAnalyzer, constants




def test_code_analyzer_trace_call_result_event_return_real():
    """
    Test if a return of a function has the correct event of return

    :return:
    """

    code_analyzer = CodeAnalyzer()
    code_analyzer.start()

    def get_int(x: int) -> int:
        return x

    get_int(1)

    code_analyzer.stop()
    code_analyzer.print()

    _list_interpretable = code_analyzer.get_list_interpretable()

    assert _list_interpretable[3].get_trace_call_result_primary().get_event() == constants.Event.RETURN


def test_code_analyzer_trace_call_result_event_return_fake():
    """
    Test if a return of a function has the correct event of line

    :return:
    """

    code_analyzer = CodeAnalyzer()
    code_analyzer.start()

    def get_int(x: int) -> int:
        x

    get_int(1)

    code_analyzer.stop()
    code_analyzer.print()

    _list_interpretable = code_analyzer.get_list_interpretable()

    assert _list_interpretable[3].get_trace_call_result_primary().get_event() == constants.Event.LINE


def test_code_analyzer_trace_call_result_using_standard_method():
    """
    Test multiple interpretables' TraceCallResults for their correct event using the code analyzer's start and stop
    methods

    :return:
    """
    code_analyzer = CodeAnalyzer()
    code_analyzer.start()

    def main():
        def primary():
            def example():
                def get(x):
                    x

                return get(1)

            example()

        return primary()

    main()

    code_analyzer.stop()
    code_analyzer.print()

    _list_interpretable = code_analyzer.get_list_interpretable()

    assert _list_interpretable[1].get_trace_call_result_primary().get_event() == constants.Event.LINE
    assert len(_list_interpretable[1].list_trace_call_result) == 1

    assert _list_interpretable[4].get_trace_call_result_primary().get_event() == constants.Event.RETURN
    assert _list_interpretable[4].list_trace_call_result[0].get_event() == constants.Event.LINE

    assert _list_interpretable[7].get_trace_call_result_primary().get_event() == constants.Event.LINE
    assert _list_interpretable[7].list_trace_call_result[1].get_event() == constants.Event.RETURN

    assert _list_interpretable[10].get_trace_call_result_primary().get_event() == constants.Event.RETURN
    assert _list_interpretable[10].list_trace_call_result[0].get_event() == constants.Event.LINE

    assert _list_interpretable[12].get_trace_call_result_primary().get_event() == constants.Event.LINE
    assert _list_interpretable[12].list_trace_call_result[1].get_event() == constants.Event.RETURN


def test_code_analyzer_trace_call_result_using_with_keyword():
    """
    Test multiple interpretables' TraceCallResults for their correct event using the code analyzer's with
    statement (Context manager)

    :return:
    """
    code_analyzer = CodeAnalyzer()

    with code_analyzer as _:
        def main():
            def primary():
                def example():
                    def get(x):
                        x

                    return get(1)

                example()

            return primary()

        main()

    code_analyzer.print()

    _list_interpretable = code_analyzer.get_list_interpretable()

    assert _list_interpretable[1].get_trace_call_result_primary().get_event() == constants.Event.LINE
    assert len(_list_interpretable[1].list_trace_call_result) == 1

    assert _list_interpretable[4].get_trace_call_result_primary().get_event() == constants.Event.RETURN
    assert _list_interpretable[4].list_trace_call_result[0].get_event() == constants.Event.LINE

    assert _list_interpretable[7].get_trace_call_result_primary().get_event() == constants.Event.LINE
    assert _list_interpretable[7].list_trace_call_result[1].get_event() == constants.Event.RETURN

    assert _list_interpretable[10].get_trace_call_result_primary().get_event() == constants.Event.RETURN
    assert _list_interpretable[10].list_trace_call_result[0].get_event() == constants.Event.LINE

    assert _list_interpretable[12].get_trace_call_result_primary().get_event() == constants.Event.LINE
    assert _list_interpretable[12].list_trace_call_result[1].get_event() == constants.Event.RETURN


def test_code_analyzer_trace_call_result_using_decorator():
    """
    Test multiple interpretables' TraceCallResults for their correct event using the code analyzer as a decorator

    IMPORTANT NOTES:
        Due to using the decorator, the Interpretable for the line of code "main()" will have an additional
        TraceCallResult where the line of code is "main()" and its Event is Return. Recall that this return is
        a fake return because the function "main()" does not return anything.

        Also, recall that all functions' last TraceCallResult will have its Event == Return regardless of having a
        explicit return line of code.

    :return:
    """
    code_analyzer = CodeAnalyzer()

    @code_analyzer
    def _main():
        def main():
            def primary():
                def example():
                    def get(x):
                        x

                    return get(1)

                example()

            return primary()

        main()

    _main()

    code_analyzer.print()

    _list_interpretable = code_analyzer.get_list_interpretable()

    assert _list_interpretable[1].get_trace_call_result_primary().get_event() == constants.Event.LINE
    assert _list_interpretable[1].list_trace_call_result[1].get_event() == constants.Event.RETURN
    assert len(_list_interpretable[1].list_trace_call_result) == 2

    assert _list_interpretable[4].get_trace_call_result_primary().get_event() == constants.Event.RETURN
    assert _list_interpretable[4].list_trace_call_result[0].get_event() == constants.Event.LINE

    assert _list_interpretable[7].get_trace_call_result_primary().get_event() == constants.Event.LINE
    assert _list_interpretable[7].list_trace_call_result[1].get_event() == constants.Event.RETURN

    assert _list_interpretable[10].get_trace_call_result_primary().get_event() == constants.Event.RETURN
    assert _list_interpretable[10].list_trace_call_result[0].get_event() == constants.Event.LINE

    assert _list_interpretable[12].get_trace_call_result_primary().get_event() == constants.Event.LINE
    assert _list_interpretable[12].list_trace_call_result[1].get_event() == constants.Event.RETURN


def test_code_analyzer_trace_call_result_class_complex_all():
    """
    Test all Interpretables and their corresponding TraceCallResults

    Notes:
        Basically test if each TraceCallResult is in the correct Interpretable along with
        testing if each Interpretable has their correct event

    :return:
    """

    code_analyzer = CodeAnalyzer()
    code_analyzer.start()

    def func():
        class Josh:
            def __init__(self):
                pass

            pass

    func()

    code_analyzer.stop()
    code_analyzer.print()

    _list_interpretable = code_analyzer.get_list_interpretable()

    assert len(_list_interpretable[0].list_trace_call_result) == 1
    assert _list_interpretable[0].list_trace_call_result[0].get_event() == constants.Event.LINE

    assert len(_list_interpretable[1].list_trace_call_result) == 1
    assert _list_interpretable[1].list_trace_call_result[0].get_event() == constants.Event.LINE

    assert len(_list_interpretable[2].list_trace_call_result) == 1
    assert _list_interpretable[2].list_trace_call_result[0].get_event() == constants.Event.CALL

    assert len(_list_interpretable[3].list_trace_call_result) == 4
    assert _list_interpretable[3].list_trace_call_result[0].get_event() == constants.Event.LINE
    assert _list_interpretable[3].list_trace_call_result[1].get_event() == constants.Event.CALL
    assert _list_interpretable[3].list_trace_call_result[2].get_event() == constants.Event.LINE
    assert _list_interpretable[3].list_trace_call_result[3].get_event() == constants.Event.RETURN

    assert len(_list_interpretable[4].list_trace_call_result) == 1
    assert _list_interpretable[4].list_trace_call_result[0].get_event() == constants.Event.LINE

    assert len(_list_interpretable[5].list_trace_call_result) == 2
    assert _list_interpretable[5].list_trace_call_result[0].get_event() == constants.Event.LINE
    assert _list_interpretable[5].list_trace_call_result[1].get_event() == constants.Event.RETURN
