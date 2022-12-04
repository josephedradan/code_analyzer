# Code Analyzer

### What is this?
A python code analyzer that allows you to visually see how your code works after executing code.
Alternatively, you can think of it as a python debugger that prints all the lines executed.

### Why would you use this?
Let's say you don't want to use a python debugger and you want to see how your code runs line by line printed out. You can import this module and add a few lines of code to initialize the analyzer and run your code, and
you will get a simple analysis of the code executed in your terminal or exported to a txt or html file. 

It is not advised to use this analyzer in a big project as the output won't fit in your terminal; though, using an export
method call to see the code in a file might be more useful/helpful.

### Requirements:
    python>=3.6
    rich
    colorama
    pandas

### Example?

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

[Example of a rich html output analyzing the file "examples/example_cursive_complex.py"](https://htmlpreview.github.io/?https://github.com/josephedradan/code_analyzer/blob/main/examples/example_cursive_complex_code_analysis_rich.html)

### Output
![example_recursive.png](./images/example_recursive.png)
### Notes

In the output of a print (Such as in the image above):

* Blue foreground code is a callable's definition.
* Green foreground code is a callable being executed.
* Red foreground text is a result of one of the method calls below:
    * .record_comment_for_interpretable_next(...) 
    * .record_comment_for_interpretable_previous(...)
    
In the output of a rich export (such as the .html files in the examples folder):

* Blue background code is a callable's definition.
* Green background code is a callable being executed.
* Orange foreground text are the current scope's variable's values/
* Red foreground text is a result of one of the method calls below:
    * .record_comment_for_interpretable_next(...) 
    * .record_comment_for_interpretable_previous(...)

__IF YOU SEE CODE THAT DOESN'T SEEM TO BE CODE THAT YOU SHOULD BE ANALYZING WHEN USING TYPE HINTING, ADD THE 
IMPORT BELOW TO THE TOP OF THE FILE TO POSSIBLY REMOVE IT__

    from __future__ import annotations



__TODO:__

