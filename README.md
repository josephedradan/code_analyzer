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
    
    def add(x: int, y: int):
        result = x + y
        code_analyzer.record_dict_for_line_previous({"result": result})
    
        for i in range(1):
            x = i
    
        return result
    
    
    add(1, 2)
    add(42, 8)
    add(5, 6)
    
    code_analyzer.stop()
    code_analyzer.print()

#### Output
![example_recursive.png](./images/example_recursive.png)