# Code Analyser

#### What is this?
Code to allow you to visually see how your code works when you run it

#### Why would you use this?
Let's say you don't want to use the debugger, and you want to see how your code runs line by line printed out easily
and neatly. You can import this module and add a few lines of code to initialize the analyzer and run your code, and
you will get a simple print analysis of your code in your terminal or in a file.

#### Example?

    from code_analyzer import CodeAnalyzer
    
    code_analyzer = CodeAnalyzer()
    code_analyzer.start()
    
    
    def recursive(depth):
        code_analyzer.record_dict_for_line_previous({"Depth": depth})
        if depth <= 0:
            return depth
    
        return recursive(depth - 1)
    
    
    recursive(5)
    
    code_analyzer.stop()
    code_analyzer.print()
    # code_analyzer.get_code_analyzer_printer().print_debug()

#### Output
![example_recursive.png](./images/example_recursive.png)