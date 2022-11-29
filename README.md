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

#### Example?

    from code_analyzer import CodeAnalyzer
    
    code_analyzer = CodeAnalyzer()  # Initialize analyzer
    code_analyzer.start()
    
    # Comment that will be displayed on the next line
    code_analyzer.record_dict_for_line_next({"Function definition here!": "Wow!"})
    
    
    def recursive(depth: int) -> int:
        # Comment that will be displayed on the previous line
        code_analyzer.record_dict_for_line_previous({"depth": depth})
        if depth <= 0:
            code_analyzer.record_dict_for_line_next({"Final depth": depth})
            return depth
    
        return recursive(depth - 1)
    
    
    code_analyzer.record_dict_for_line_next({"This is where the fun begins": "Oh no!"})
    recursive(5)
    
    code_analyzer.stop()
    code_analyzer.print()

#### Output
![example_recursive.png](./images/example_recursive.png)


__TODO:__
- Support code_analyzer.record_str_for_line_next("Hello world")
- Support code_analyzer.record_str_for_line_previous("Hello world")
- Support code_analyzer.hide_line_previous(amount)
- Support code_analyzer.hide_line_next(amount)
