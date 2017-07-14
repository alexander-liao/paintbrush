# paintbrush
Paintbrush is a partially stack-based recreational golfing language specifically made for ASCII-art code-golf challenges. It attempts to specialize in kolmogorov-complexity challenges but also supports ASCII-art challenges with user input.

## usage
To use Paintbrush, download `paintbrush.py` and `evaluator.py` into the same directory. Python 3 is required for Paintbrush. The following modules need to be loaded: `sys`, `re`, `ast`.

To run a program, do `python paintbrush.py <flags> <filename/program> <arg1>...`. The flags are as follows, with the recommended settings bolded:

Flag|Description|Description of not using this flag
----|-----------|------------------
`f`|**Read from the file given in argument 4** |Use argument 4 as the program itself
`u`|**Use unicode encoding** |Use Paintbrush codepage encoding
`n`|**Append a newline to the final output** |Don't append a newline to the final output
`k`|**Remove whitespace to the right of the program** |Keep the program as-is
`y`|Debug mode|**Normal mode**

To run `program.pb` with unicode encoding, appending a newline to the output, and right-stripping the program first, you would run the command `python paintbrush.py funk program.pb`. Note that `fun` means "use file and unicode and append newline", `funk` means "use file and unicode and append newline and right-strip program", and `funky` means "use file and unicode and append newline and right-strip program in debug mode". To debug a file in unicode mode with a trailing newline without right-stripping the program, I strongly recommend using `funny` over `funy` because duplicate flags are ignored.

## syntax
Certain commands will read ahead and take the next character even if it would otherwise be a command (for golfing; that way, one does not need to use character syntax, which would cost one byte). Exceptions are when the next character is one of 0123456789({$' because those have special meanings. Note that these commands won't use the next character ahead if it already has a single-character string on the stack, but that won't break anything until I add multibyte commands, in whch case I can easily make an exception by adding more characters to the `0123456789({$'` list.

The `s`, `b`, and `=` commands will read ahead.

### syntax | integers
For the most part, the only numbers you will need are integers. Note that a float that is technically an integer will behave as a float and not work for many operations. An integer must match the regular expression `\\d+`.

### syntax | floats
Floats are only used when doing arithmetic operations; operations that take an optional integer to determine the number of repetitions of a command ignore floats even if they are technically integers. A float must match the regular expression `\\d+(\\.\\d*)?|\\d*\\.\\d+`, meaning it may be in the form `0.0`, `0.`, or `.0`.

### syntax | strings
Strings are used for many different applications and will be taken as a stack argument to many operations. Note that this does support backslash escaping. A string must match the regular expression `\"(\\.|[^\"])+\"`.

### syntax | single-character strings
Single-character strings are used for certain operations such as the `set-character` and `set-background` operations. A single-character string may also be denoted with `'?` where `?` represents the character. Note that this does not support backslash escaping. A single-character string must match the syntax `'.`.

### syntax | single-character escaped strings
A single-character string containing an escaped character can be denoted as ``` `?``` where `?` represents the escaped character. For example, ``` `n``` would become a newline.

### syntax | variables
A variable has a single-character name, though not necessarily a single-byte name (note though that using variable names outside of the Paintbrush code page is quite expensive in terms of byte count). Note that variables may not be named digits, because those represent function arguments. A variable must match the regular expression `\$\D`.

### syntax | comments
Comments are supported in Paintbrush without a heavy loss for golfing. A comment is simply a piece of arbitrary text delimited by two spaces on either side, or starting with two spaces and ending at the end of the file. Note that you will need more spaces if one of the leading spaces is consumed by one of the read-ahead operators.

### syntax | other
`;` - A semicolon will do nothing other than delimit two things that would otherwise be combined, such as two adjacent numbers. A regular space (not a double space) will behave like any other character.  
`(...)` - Brackets surrounding something will make it become an evaluated statement; that is, if it is surrounded in brackets, the interpreter will take the entire token (including the brackets) and evaluate it. However, this only works for literals as defined by `ast.literal_eval`.  
`{...}` - Curly braces surrounding some code will become a function. Normally, these are just run, but using `$1...$n`, you can pass objects into these functions through the stack. If an integer is on the top of the stack when the function is declared and run (status-planned: allow declaration of functions and reuse later), then the function will be run that many times with an incrementer `$0` to count the number of iterations so far. If none of `$1...$n` are used in a function, the top of the stack will not popped off. Note that the number of repetitions is popped off first.  

## stack
The stack can contain any Python object, but it should not end up with anything other than strings, numbers, and maybe Paintbrush Function Objects. Theoretically, using the evaluate input command could mess that up, but then commands just simply won't use the stack. If the current token is not a string, then it cannot be a command and is automatically pushed to the stack. If the token is a string but is not recognized as a command, then it is pushed to the stack. You can explicitly push the next token to the stack using `»`. You can discard the top of the stack using `«`. The stack will give `None` if you try to pop it while it is empty, but will not throw an error (this will usually result in the command ignoring it).

## grid
As this is an ASCII-art language, the working surface is a 2D grid of single characters (it is possible to end up with multiple characters in one grid space, but that's not supposed to happen, though if the programmer decides to do that, it is very much possible and very easy; `"hi"=as$a` will do it). Commands can manipulate the grid and where the pointer is. The pointer starts at `(0, 0)` and the grid starts as `[[' ']]`. There is also a background variable which can be updated to change the background of the grid. If a character is not modified, it will be changed when the background is updated.

## commands
Command|Description
-------|-----------
`s?`|Sets the current grid space to `?`. If the current top-of-stack is a single-character string, then `?` is not required; `s` will read off of the stack.
`b?`|Sets the background to `?` and updates all unmodified spaces. If the current top-of-stack is a single-character string, then `?` is not required; `b` will read off of the stack.
`l`|If the current top-of-stack is a string, set it to all lowercase; otherwise, set the current grid space to lowercase
`u`|If the current top-of-stack is a string, set it to all uppercase; otherwise, set the current grid space to uppercase
`æ`|Push the lowercase alphabet
`Æ`|Push the uppercase alphabet
`=?`|Sets the value of the variable `$?` to the top of the stack. If the current top-of-stack is a single-character string, then `?` is not required; `=` will read off of the stack. The variable name will be removed first so if you need to set the value of variable `$?` to a single character string, then `=?` will not work but `'?=` will.
`+`|`push(pop() + pop())` ; addition
`-`|`push(pop() - pop())` ; subtraction
`*`|`push(pop() ** pop())` ; exponentiation
`×`|`push(pop() * pop())` ; multiplication
`:`|`push(pop() // pop())` ; floor division
`÷`|`push(pop() / pop())` ; float division
`¥`|`push(str(pop()))` ; Python string representation
`£`|`push(input())` ; Reads a single line of input without the trailing newline
`€`|`push(ast.literal_eval(input()))` ; Reads a single line of input without the trailing newline and evaluates it as a Python literal
`Ø`|`push(eval(input()))` ; Reads a single line of input without the trailing newline and unsafely evaluates it. Note that `eval` is not actually used in the interpreter; it is redirected to another file to avoid programs reading off variables from the interpreter.
`Ñ`|`push(sys.stdin.readline())` ; Reads a line from STDIN which includes the trailing newline
`ñ`|`push(sys.stdin.read(1))` ; Reads a single character from STDIN
`Œ`|Reads a single character from STDIN and returns the value held by that variable
`↓↑←→`|If the current top-of-stack is an integer, move the pointer that many spaces in the indicated direction. If the current top-of-stack is a string, move the pointer along and write out the string in the indicated direction. Otherwise, move the pointer 1 space. This will push the grid boundaries if necessary.
`⇩⇧⇦⇨`|Same as above but this will wrap around the grid boundaries if necessary.
`▁▔▏▕`|If the current top-of-stack is an integer, remove that many rows/columns from the indicated side of the grid. Otherwise, remove 1.
`▄▀▌▐`|Mirror the entire grid, duplicating the innermost edge. `▄` will copy the top edge to the bottom. This will change some characters that have backwards versions, unless the modifier is true.
`┻┳┫┣`|Mirror the entire grid, overlapping the innermost edge. `┻` will copy the top edge to the bottom. This will change some characters that have backwards versions, unless the modifier is true.
`━`|If the current top-of-stack is an integer, delete `2 * top - 1` rows centered around the current row, moving the pointer up as necessary if it ends up off of the grid. Otherwise, remove 1.
`┃`|If the current top-of-stack is an integer, delete `2 * top - 1` columns centered around the current column, moving the pointer left as necessary if it ends up off of the grid. Otherwise, remove 1.
`┴┬┤├`|If the current top-of-stack is an integer, insert that many extra rows/columns in the direction of the short leg of the symbol. Otherwise, insert 1.
`┷┯┨┠`|If the current top-of-stack is an integer, copy the current row/column that many times in the direction of the short leg of the symbol. Otherwise, copy once.
`↧↥↤↦`|If the current top-of-stack is an integer, copy the entire grid that many times in the direction of the arrow. Otherwise, copy once.
`⇓⇑⇐⇒`|If the current top-of-stack is an integer, copy each individual row/column that many times in the direction of the arrow. Otherwise, copy each once.
`═`|If the current top-of-stack is an integer, erase `2 * top - 1` rows centered around the current row, without modifying the size of the grid (and catching any `IndexError`). Otherwise, erase 1.
`║`|If the current top-of-stack is an integer, erase `2 * top - 1` columns centered around the current column, without modifying the size of the grid (and catching any `IndexError`). Otherwise, erase 1.
`»`|Push the next token onto the stack
`«`|Pop the top of the stack and discard it
`↶`|Move the pointer back to where it was before the last command, which rotates the `hist` variable forward by 1.
`↷`| Move the pointer to where it was before the last undo, which rotates the `hist` variable backward by 1.
`!`|Sets the entire grid to foreground mode, so the `b` command will only affect future operations.
`¡`|Sets the entire grid to background mode, so the `b` command would erase everything.
`?`|Sets every space that has the current background character in it to background mode even if it was set there manually.
`@`|Swaps the top two elements on the stack
`¦`|Stringify the top of the stack and then push each character individually in reverse order so that the first character becomes the new top of the stack.
`¿{...}`|Runs the code block if and only if the top of the stack represents True. The top of the stack can be retrieved from within the code block using `$0`. A normal command may be used as well if it forms a single block and does not require arguments. Does not pop the top of the stack off.
`¤{...}`|Runs the code block if and only if the top of the stack represents False. The top of the stack can be retrieved from within the code block using `$0`. A normal command may be used as well if it forms a single block and does not require arguments. Does not pop the top of the stack off.
`œ`|Sets the modifier to true, which is always set back to false by the next command regardless of whether or not it actually makes a difference.

## examples
These are some examples of some things that you can do with Paintbrush. The first section consists of basic test programs, and the second part moves into ASCII-art, which is what this language is really all about.

### hello world program #1
Hello World programs are common beginner programs because they demonstrate an introduction to the syntax of the language (except in Python because it's too easy; I was talking more verbose languages like Java :P). They are also good tests to make sure that the language hasn't been completely destroyed. The simplest Hello World program in Paintbrush is:

        "Hello, World!"→

Beats Python :D

This doesn't really print `"Hello, World!"` ; rather, it writes it over the grid and then the grid is packed together and printed.

### hello world program #2
Of course, you could also set each character individually if you really wanted to:

        sH→se→sl→sl→so→s,→s →sW→so→sr→sl→sd→s!

This sets each individual space to the characters, and it has to explicitly move right each time. Beats Brainf**k :D

### hello world program #3
You can never have too many ways of printing `"Hello, World!"` :P

        blsH→se3→so→s,→s →sW→so→sr→sl→sd→s!

This is mostly just a way to test that `b` still works. It sets the background to `l` and then writes `"He__o, World!"` which becomes `"Hello, World!"` with the background. Beats method 2 apparently :o

### arithmetic operations test

        2;3+¥→  you can replace + with other operations

This tests to make sure the operations (and the `str` command) still work :P

### add user input

        €€@+¥→  you can replace + with other operations

This evaluate-inputs twice, and then adds them together, stringifies it and writes it to the right. The swap isn't necessary for some operations but this way you can test it on an operation.

### alphabet spiral

        æ¦→↑←←↓↓→→→↑↑↑←←←←↓↓↓↓→→→→→↑

Pushes the alphabet, splits it all 26 segments, and then draws the spiral out manually.
