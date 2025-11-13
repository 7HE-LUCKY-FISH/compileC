# compileC - Python C Compiler

A Python-based educational compiler that demonstrates the **5 stages of compilation** for C code.

## Overview

This compiler implements all five classic stages of compilation:

1. **Lexical Analysis (Scanner)** - Tokenizes the source code
2. **Syntax Analysis (Parser)** - Builds an Abstract Syntax Tree (AST)
3. **Semantic Analysis** - Type checking and symbol table construction
4. **Intermediate Code Generation** - Generates Three-Address Code (TAC)
5. **Code Generation & Optimization** - Produces assembly-like target code

## Features

- ✅ Complete lexical analysis with keyword, operator, and literal recognition
- ✅ Recursive descent parser for C syntax
- ✅ Symbol table management and semantic checking
- ✅ Three-address code intermediate representation
- ✅ Assembly-like code generation
- ✅ Basic code optimization (constant folding, dead code elimination)
- ✅ Clear visualization of each compilation stage

## Requirements

- Python 3.7 or higher
- No external dependencies required!

## Installation

```bash
git clone https://github.com/7HE-LUCKY-FISH/compileC.git
cd compileC
```

## Usage

### Run with Built-in Example

```bash
python compiler.py --example
```

### Compile a C File

```bash
python compiler.py examples/factorial.c
```

### Quiet Mode (Less Verbose Output)

```bash
python compiler.py examples/factorial.c --quiet
```

### Command Line Options

```
usage: compiler.py [-h] [-q] [-e] [input_file]

C Compiler - Demonstrates 5 stages of compilation

positional arguments:
  input_file     Input C source file

optional arguments:
  -h, --help     show this help message and exit
  -q, --quiet    Suppress detailed stage output
  -e, --example  Run with built-in example
```

## Examples

The `examples/` directory contains sample C programs:

- `factorial.c` - Recursive factorial function
- `arithmetic.c` - Basic arithmetic operations
- `loop.c` - While loop example

## Supported C Features

### Data Types
- `int` - Integer type
- `float` - Floating-point type
- `char` - Character type
- `void` - Void type (for functions)

### Operators
- Arithmetic: `+`, `-`, `*`, `/`, `%`
- Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Logical: `&&`, `||`, `!`
- Assignment: `=`

### Control Structures
- `if` / `else` statements
- `while` loops
- `for` loops
- `return` statements

### Functions
- Function declarations
- Function calls
- Parameters and return values

## Compilation Stages Explained

### Stage 1: Lexical Analysis
Converts source code into tokens (keywords, identifiers, operators, literals).

**Example:**
```c
int x = 5;
```
Produces tokens: `INT`, `IDENTIFIER(x)`, `ASSIGN`, `INTEGER_LITERAL(5)`, `SEMICOLON`

### Stage 2: Syntax Analysis
Parses tokens into an Abstract Syntax Tree (AST) based on C grammar rules.

**Example AST:**
```
Program
  VarDecl: int x
    Initializer:
      IntLiteral: 5
```

### Stage 3: Semantic Analysis
Checks for semantic errors, builds symbol tables, and performs type checking.

**Checks:**
- Variable declarations
- Type compatibility
- Function signatures
- Scope rules

### Stage 4: Intermediate Code Generation
Generates Three-Address Code (TAC), a platform-independent intermediate representation.

**Example TAC:**
```
x = 5
t0 = x + 1
return t0
```

### Stage 5: Code Generation & Optimization
Generates assembly-like target code and applies optimizations.

**Example Assembly:**
```assembly
LOAD R0, #5
MOV R1, R0
ADD R1, #1
MOV RAX, R1
```

## Project Structure

```
compileC/
├── compiler.py              # Main compiler driver
├── lexer.py                 # Stage 1: Lexical Analysis
├── parser.py                # Stage 2: Syntax Analysis
├── semantic_analyzer.py     # Stage 3: Semantic Analysis
├── intermediate_code.py     # Stage 4: Intermediate Code Generation
├── code_generator.py        # Stage 5: Code Generation & Optimization
├── examples/                # Example C programs
│   ├── factorial.c
│   ├── arithmetic.c
│   └── loop.c
└── README.md
```

## Educational Purpose

This compiler is designed for educational purposes to help understand how compilers work. It demonstrates:

- How source code is transformed through multiple stages
- The role of each compilation stage
- How intermediate representations simplify code generation
- Basic optimization techniques

## Limitations

This is an educational compiler and does not support:
- Pointers and arrays
- Structs and unions
- Preprocessor directives
- Standard library functions (except demonstration purposes)
- Complex expressions and type casting
- Multiple source files

## Sample Output

When you run the compiler, you'll see detailed output for each stage:

```
================================================================================
 C COMPILER - 5 STAGES OF COMPILATION
================================================================================

================================================================================
 STAGE 1: LEXICAL ANALYSIS (Scanner)
================================================================================

=== STAGE 1: LEXICAL ANALYSIS ===
Token Type           Value           Line   Column
-------------------------------------------------------
INT                  int             1      1
IDENTIFIER           factorial       1      5
...

================================================================================
 STAGE 2: SYNTAX ANALYSIS (Parser)
================================================================================

Abstract Syntax Tree (AST):
------------------------------------------------------------
Program
  FunctionDecl: int factorial
    Parameters:
      Parameter: int n
    Body:
      CompoundStmt
...

================================================================================
 STAGE 3: SEMANTIC ANALYSIS
================================================================================

=== STAGE 3: SEMANTIC ANALYSIS ===
Symbol Table:
Name                 Type                 Scope
------------------------------------------------------------
factorial            function:int         global
n                    int                  function:factorial
...

================================================================================
 STAGE 4: INTERMEDIATE CODE GENERATION
================================================================================

=== STAGE 4: INTERMEDIATE CODE GENERATION ===
Three-Address Code (TAC):
------------------------------------------------------------
  function factorial:
  t0 = n <= 1
  ifFalse t0 goto L0
...

================================================================================
 STAGE 5: CODE GENERATION AND OPTIMIZATION
================================================================================

=== STAGE 5: CODE OPTIMIZATION ===
Optimization Techniques Applied:
  - Constant folding
  - Dead code elimination
  - Redundant load elimination
...

=== STAGE 5: CODE GENERATION ===
Generated Assembly Code:
------------------------------------------------------------
; Generated Assembly Code
; Simplified RISC-style instructions

; Function: factorial
factorial:
    PUSH BP
    MOV BP, SP
...

================================================================================
 COMPILATION COMPLETED SUCCESSFULLY!
================================================================================
```

## Contributing

This is an educational project. Feel free to fork and enhance it with additional features!

## License

This project is open source and available for educational purposes.

## Author

7HE-LUCKY-FISH

## References

- Compilers: Principles, Techniques, and Tools (Dragon Book)
- Modern Compiler Implementation in C/Java/ML
- Engineering a Compiler