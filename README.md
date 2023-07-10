# Creating My Own Programming Language: ShenShenPL

ShenShenPL is a new programming language, along with its unique grammar and syntax, that allows users to write and execute computer programs. Implemented by Python, it offers a clean and intuitive syntax that makes it easy for both beginners and experienced programmers to write elegant and maintainable code. This README file provides an overview of the language, its usage, functionality, and syntax.

## Installation

To use ShenShenPL, follow these steps:

1. You need to have Python installed on your system. You can download Python from the official website: [https://www.python.org/downloads/](https://www.python.org/downloads/)

2. Clone ShenShenPL Git repository using the following command:

    ```shell
    git clone https://github.com/SHENSHENZYC/my-programming-language
    ```

3. Navigate to the cloned repository:

    ```shell
    cd my-programming-language
    ```

## Usage

Once you have navigated to the ShenShenPL repository, you can start the ShenShenPL interactive shell by executing the following command:

```shell
python shell.py
```

This will activate the ShenShenPL interactive shell, where you can write and execute ShenShenPL code.

Inside the shell, you have two options for executing ShenShenPL code:

1. Single-line or multi-line code execution: Write a single-line code directly or a multi-line code by separating lines with `;` in the shell and press enter to execute it. For example:

    ```sspl
    shell> 1 + 2 * 3        # single-line code
    7
    shell> 1 + 2; 3 * 4; 5 + 6 * 7      # multi-line code
    [3, 12, 47]
    ```

2. Running a script file: Save your ShenShenPL script inside a .ss file (e.g., program.ss), and then run the file by entering the following command in the shell:

    ```sspl
    shell> run("program.ss")
    ```

    Replace program.ss with the name of your script file.

Using either of these methods, you can write and execute ShenShenPL code within the interactive shell.

## Syntax

The syntax of ShenShenPL is as follows:

### Comments

Use the `#` symbol to add comments to your code. Comments are ignored by the interpreter and are used to provide explanations or make notes in your code.

```sspl
shell> # This is a comment in ShenShenPL
```

### Print Statement

To output a message to the console, use the `print` function and pass in the message you want to display.

```sspl
shell> print("Hello, world!")
Hello, world!
```

### Variables

Variables are used to store and manipulate data in ShenShenPL. To declare a variable, use the `var` keyword followed by the variable name and its initial value.

```sspl
shell> var x = 10
10
shell> var message = "Hello, world!"
"Hello, world!"
```

### Arithmetic Operations

ShenShenPL supports basic arithmetic operations:

- Addition: `+`
- Subtraction: `-`
- Multiplication: `*`
- Division: `/`
- Power: `^`
- Parentheses: `()`

```sspl
shell> var x = 3 + 5     # x = 8
8
shell> var y = x * 2     # y = 16
16
shell> var z = y / 4     # z = 4.0
4.0
```

### Conditional Statements

You can use `if` statements to conditionally execute code based on a condition. Use keyword `and`, `or`, `not` for manipulating boolean expressions.

```sspl
shell> var x = 10
10
shell> if x < 5 then print("x is greater than 5") elif x >= 5 and x < 8 then print("x is greater than or equal to 5 and less than 8") else print("x is greater than or equal to 8")
x is greater than or equal to 8
```

Note that keyword `end` is not required for single-line if statements, but is required for multi-line if statements:

```sspl
shell> if x < 5 then; print("x is greater than 5"); elif x >= 5 and x < 8 then; print("x is greater than or equal to 5 and less than 8"); else; print("x is greater than or equal to 8"); end;
x is greater than or equal to 8
```

Single-line if statements can be treated as values that can be assigned to variables or used in arithmetic expressions:

```sspl
shell> var x = 10
10
shell> var y = (if x < 5 then 2 * x else x / 2) + 2   # y = 7.0
7.0
```

### Loops

ShenShenPL supports `for` and `while` loops for iteration.

#### For Loop

The `for` loop iterates over a range of values.

```sspl
shell> for i = 1 to 5 do print(i)
1
2
3
4
```

There is an optional keyword `step` that can be used to specify the step size for the loop:

```sspl
shell> for i = 1 to 5 step 2 do print(i)
1
3
```

_NOTE_: Omitting the `step` keyword is equivalent to setting the step size to 1.

Similar to if statements, the `end` keyword is not required for single-line for loops, but is required for multi-line for loops:

```sspl
shell> for i = 1 to 5 do; print(i); end;
1
2
3
4
```

#### While Loop

The `while` loop executes a block of code as long as a condition is true.

```sspl
shell> var x = 0
0
shell> while x < 5 do var x = x + 1
[1, 2, 3, 4, 5]
```

Similar to if statements and for loops, the `end` keyword is not required for single-line while loops, but is required for multi-line for loops:

```sspl
shell> while x < 5 do; var x = x + 1; end;
[1, 2, 3, 4, 5]
```

#### Break and Continue

You can use the `break` keyword to exit a loop and the `continue` keyword to skip the current iteration of a loop.

```sspl
shell> for i = 1 to 5 do; if i == 3 then; break; else; print(i); end; end;
1
2
```

```sspl
shell> for i = 1 to 5 do; if i == 3 then; continue; else; print(i); end; end;
1
2
4
```

_NOTE_: You can only use `break` and `continue` inside a loop (either a for loop or a while loop).

### Data Types

ShenShenPL supports numerous data types, including `int`, `float`, `string`, and `list`. We talked about `int` and `float` when we introduced arithmetic expressions. Here we will discuss `string` and `list` and their respective operations.

#### String

A string is a sequence of characters enclosed in double quotes. A string can be assigned to a variable:

```sspl
shell> var message = "Hello, world!"
"Hello, world!"
```

You can use the `+` operator to concatenate two strings:

```sspl
shell> var message = "Hello, " + "world!"
"Hello, world!"
```

You can use the `*` operator with a scalar to repeat a string:

```sspl
shell> var message = "Hello, " * 3
"Hello, Hello, Hello, "
```

#### List

A list is a sequence of values enclosed in square brackets. A list can be assigned to a variable:

```sspl
shell> var numbers = [1, 2, 3, 4, 5]
[1, 2, 3, 4, 5]
```

You can use the `+` operator to append an additional element to a list:

```sspl
shell> var numbers = [1, 2, 3, 4] + 5
[1, 2, 3, 4, 5]
```

You can use the `-` operator with an index to remove an element of the given index from a list:

```sspl
shell> var numbers = [1, 2, 3, 4]
[1, 2, 3, 4]
shell> var numbers = numbers - 2
[1, 2, 4]
```

You can use the `*` operator to concatenate two lists:

```sspl
shell> var numbers = [1, 2, 3] * [4, 5, 6]
[1, 2, 3, 4, 5, 6]
```

You can use the `/` operator with an index to access an element of the given index from a list:

```sspl
shell> var numbers = [1, 2, 3, 4]
[1, 2, 3, 4]
shell> var x = numbers / 2
3
```

_NOTE_: The index provided for the `-` or `/` operator cannot exceed the number of elements - 1, or you will raise an error, and stop the execution of your ShenShenPL program.

### Functions

ShenShenPL supports functions. A function is a block of code that can be called from other parts of the program. A function can take in parameters and return a value.

#### Defining a Function

A function in ShenShenPL can be defined in either a single-line manner or a multi-line manner. For single-line function definition, you can use a keyword `func` followed by an optional function name, a list of arguments inside parentheses, an arrow `->`, and the function body. The function body can contain multiple statements and will be executed when the function is called. For example, if we would like to define a function that takes two numbers and return their sum, we can do the following:

```sspl
shell> func add(a, b) -> a + b
<function add>
```

For multi-line definition, if we would like to define a function with the same functionality:

```sspl
shell> func add(a, b); var c = a + b; return c; end;
<function add>
```

_NOTE_: The `return` keyword and the `end` keyword is required for multi-line function definition, but is not allowed for single-line function definition. On the other hand, `->` is requited for single-line function definition.

#### Calling a Function

A function can be called by using its name followed by a list of arguments inside parentheses. For example, if we would like to call the function `add` that we defined above:

```sspl
shell> add(1, 2)
3
```

We can also assign a function to a variable and call it by referring the variable:

```sspl
shell> var add_copy = func add(a, b) -> a + b
<function add>
shell> add_copy(1, 2)
3
```

Note that function name is optional when defining a function, so when we omit function name when defining one, we can assign the function to a variable and call it by referring the variable:

```sspl
shell> var add = func (a, b) -> a + b
<function add>
shell> add(1, 2)
3
```

## Examples

To help you get started with ShenShenPL, we have provided an example script called example.ss in the ShenShenPL Git repository. You can run the example script using the following command in the ShenShenPL shell:

```sspl
run("examples/example.ss")
```

This script showcases various features of ShenShenPL and serves as a reference for understanding the language's syntax and capabilities. Feel free to explore the example script and modify it to experiment with different code patterns and language features.

## Limitations

ShenShenPL is a simple programming language designed for learning purposes. It may not have all the features or capabilities of a fully-fledged programming language. It is recommended to use it for small projects or educational purposes.

## Contributing

If you find any bugs or have suggestions for improvements, feel free to open an issue or submit a pull request on the GitHub repository: [https://github.com/SHENSHENZYC/my-programming-language](https://github.com/SHENSHENZYC/my-programming-language)

## License

This project is licensed under the [MIT License](LICENSE).
