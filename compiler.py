#!/usr/bin/env python3
"""
Main Compiler Driver
Demonstrates the 5 stages of a compiler for C code
"""

import sys
import argparse
from pathlib import Path

from lexer import Lexer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer
from intermediate_code import IntermediateCodeGenerator
from code_generator import CodeGenerator


def compile_c_code(source_code: str, show_stages: bool = True):
    """
    Compile C source code through all 5 stages
    
    Args:
        source_code: The C source code to compile
        show_stages: Whether to print output from each stage
    """
    
    print("=" * 80)
    print(" C COMPILER - 5 STAGES OF COMPILATION")
    print("=" * 80)
    
    try:
        # Stage 1: Lexical Analysis
        if show_stages:
            print("\n" + "=" * 80)
            print(" STAGE 1: LEXICAL ANALYSIS (Scanner)")
            print("=" * 80)
        
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        
        if show_stages:
            lexer.print_tokens()
            print(f"\nTotal tokens generated: {len(tokens)}")
        
        # Stage 2: Syntax Analysis
        if show_stages:
            print("\n" + "=" * 80)
            print(" STAGE 2: SYNTAX ANALYSIS (Parser)")
            print("=" * 80)
        
        parser = Parser(tokens)
        ast = parser.parse()
        
        if show_stages:
            print("\nAbstract Syntax Tree (AST):")
            print("-" * 60)
            parser.print_ast(ast)
        
        # Stage 3: Semantic Analysis
        if show_stages:
            print("\n" + "=" * 80)
            print(" STAGE 3: SEMANTIC ANALYSIS")
            print("=" * 80)
        
        semantic_analyzer = SemanticAnalyzer()
        semantic_analyzer.analyze(ast)
        
        if show_stages:
            semantic_analyzer.print_symbol_table()
            print("\nSemantic analysis completed successfully!")
        
        # Stage 4: Intermediate Code Generation
        if show_stages:
            print("\n" + "=" * 80)
            print(" STAGE 4: INTERMEDIATE CODE GENERATION")
            print("=" * 80)
        
        code_gen = IntermediateCodeGenerator()
        code_gen.generate(ast)
        
        if show_stages:
            code_gen.print_tac()
            print(f"\nTotal TAC instructions generated: {len(code_gen.instructions)}")
        
        # Stage 5: Code Generation and Optimization
        if show_stages:
            print("\n" + "=" * 80)
            print(" STAGE 5: CODE GENERATION AND OPTIMIZATION")
            print("=" * 80)
        
        target_code_gen = CodeGenerator(code_gen.instructions)
        target_code_gen.generate()
        target_code_gen.optimize()
        
        if show_stages:
            target_code_gen.print_assembly()
        
        print("\n" + "=" * 80)
        print(" COMPILATION COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        
        return True
        
    except SyntaxError as e:
        print(f"\n❌ Compilation Error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point for the compiler"""
    parser = argparse.ArgumentParser(
        description='C Compiler - Demonstrates 5 stages of compilation'
    )
    parser.add_argument(
        'input_file',
        nargs='?',
        help='Input C source file'
    )
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Suppress detailed stage output'
    )
    parser.add_argument(
        '-e', '--example',
        action='store_true',
        help='Run with built-in example'
    )
    
    args = parser.parse_args()
    
    # Built-in example
    if args.example or not args.input_file:
        print("Using built-in example C code...")
        source_code = """
int factorial(int n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

int main() {
    int x;
    x = 5;
    int result;
    result = factorial(x);
    return result;
}
"""
        compile_c_code(source_code, show_stages=not args.quiet)
    else:
        # Read from file
        input_path = Path(args.input_file)
        if not input_path.exists():
            print(f"Error: File '{args.input_file}' not found")
            sys.exit(1)
        
        try:
            with open(input_path, 'r') as f:
                source_code = f.read()
            
            print(f"Compiling: {input_path}")
            print(f"Source code length: {len(source_code)} characters\n")
            
            success = compile_c_code(source_code, show_stages=not args.quiet)
            sys.exit(0 if success else 1)
            
        except IOError as e:
            print(f"Error reading file: {e}")
            sys.exit(1)


if __name__ == '__main__':
    main()
