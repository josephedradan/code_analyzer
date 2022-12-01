# Code Analyser

#### What is this?
A Python code that allows you to visually see how your code works after the execution of your code.

#### Why would you use this?
Let's say you don't want to use the debugger, and you want to see how your code runs line by line printed out easily
and neatly. You can import this module and add a few lines of code to initialize the analyzer and run your code, and
you will get a simple print analysis of your code in your terminal or in a file.

#### Requirements:
    python>=3.6
    rich
    colorama
    pandas

#### Example?

    from code_analyzer import CodeAnalyzer
    
    code_analyzer = CodeAnalyzer()
    code_analyzer.start()
    
    
    def add(x: int, y: int):
        result = x + y
        code_analyzer.record_comment_for_interpretable_previous({"result": result})
        code_analyzer.record_comment_for_interpretable_previous(f"Result {result}")
    
        for i in range(1):
            x = i
    
        return result
    
    
    add(1, 2)
    add(42, 8)
    add(5, 6)
    
    code_analyzer.stop()
    code_analyzer.print()

Or just look at the other examples in examples folder.


#### Output
![example_recursive.png](./images/example_recursive.png)
#### Notes

In the output of a print (Such as in the image above):

* Blue foreground code is a callable's definition.
* Green foreground code is a callable being executed.
* Red background code is a result of one of the method calls below:
    * .record_comment_for_interpretable_next(...) 
    * .record_comment_for_interpretable_previous(...)
    
In the output of a rich export (such as the .html files in the examples folder):

* Blue background code is a callable's definition.
* Green background code is a callable being executed.
* Red background code is a result of one of the method calls below with an argument having the type of dict:
    * .record_comment_for_interpretable_next(...) 
    * .record_comment_for_interpretable_previous(...)
    
* Orange background code is a result of one of the method calls below with an argument having the type that is not a dict:
    * .record_comment_for_interpretable_next(...) 
    * .record_comment_for_interpretable_previous(...)

__TODO:__

