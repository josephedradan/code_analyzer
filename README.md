
# Code Analyzer

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/python-code-analyzer)
[![PyPI version](https://badge.fury.io/py/python-code-analyzer.svg)](https://badge.fury.io/py/python-code-analyzer)
[![tests](https://github.com/josephedradan/code_analyzer/actions/workflows/test.yml/badge.svg)](https://github.com/josephedradan/code_analyzer/actions/workflows/test.yml)
![PyPI - Status](https://img.shields.io/pypi/status/python-code-analyzer)
![PyPI - License](https://img.shields.io/pypi/l/python-code-analyzer)

### What is this?
A python code analyzer that allows you to visually see how your code works after executing code.
Alternatively, you can think of it as a python debugger that prints all the lines executed.

### Why would you use this?
Let's say you don't want to use a python debugger and you want to see how your code runs line by line printed out. You can import this module and add a few lines of code to initialize the analyzer and run your code, and
you will get a simple analysis of the code executed in your terminal or exported to a txt or html file. 

It is not advised to use this analyzer in a big project as the output won't fit in your terminal; though, using an export
method call to see the code in a file might be more useful/helpful.

### Requirements:
https://github.com/josephedradan/code_analyzer/blob/e2492649865b50f51d970be3c6d06d433d03596e/requirements.txt#L1-L4

### Example:

https://github.com/josephedradan/code_analyzer/blob/571b6c716fbc444bb5307c06e2689cea4c010d4a/examples/example_recursive.py#L24-L53

### Output

![example_recursive.png](https://raw.githubusercontent.com/josephedradan/code_analyzer/main/images/example_recursive.png)

## [Rich output html](https://htmlpreview.github.io/?https://github.com/josephedradan/code_analyzer/blob/main/examples/example_recursive_code_analysis_rich.html)
### Notes

In the output of a print (Such as in the image above):

* Blue foreground code is a callable's definition.
* Green foreground code is a callable being executed.
* Red foreground text are {Variable: value} pairs found in between the `{}` brackets that are new to the current interpretable relative to its scope. 
* Purple foreground text are (arguments) found in between the `()` brackets passed to the method calls below:
    * .record_comment_for_interpretable_next(...) 
    * .record_comment_for_interpretable_previous(...)
    
In the output of a rich export (such as the .html files in the examples folder):

* Blue background code is a callable's definition.
* Green background code is a callable being executed.
* Orange foreground text are {Variable: value} pairs found in between the {} brackets that are new to the current interpretable relative to its scope. 
* Red foreground text are (arguments) found in between the () brackets passed to the method calls below:
    * .record_comment_for_interpretable_next(...) 
    * .record_comment_for_interpretable_previous(...)

__IF YOU SEE CODE THAT DOESN'T SEEM TO BE CODE THAT YOU SHOULD BE ANALYZING WHEN USING TYPE HINTING, ADD THE 
IMPORT BELOW TO THE TOP OF THE FILE TO POSSIBLY REMOVE IT__

    from __future__ import annotations

### Installation
    pip install python-code-analyzer

### [pypi](https://pypi.org/project/python-code-analyzer/)

__TODO:__
* Fancy visualizer
* Memory usage?
* Timing code?
* profiler (Time and calls amount)
* dis.show_code 
* 03/04/2025 			

        Project similar to Python Code Analyzer https://pythontutor.com/ use this as reference as you make yours
			