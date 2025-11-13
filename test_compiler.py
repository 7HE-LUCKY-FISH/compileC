#!/usr/bin/env python3
"""
Test suite for the C compiler
Tests all 5 stages of compilation
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import Lexer, TokenType
from parser import Parser
from semantic_analyzer import SemanticAnalyzer, SemanticError
from intermediate_code import IntermediateCodeGenerator
from code_generator import CodeGenerator


def test_lexer():
    """Test lexical analysis"""
    print("Testing Stage 1: Lexical Analysis...")
    
    # Test basic tokenization
    source = "int x = 5;"
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    
    assert tokens[0].type == TokenType.INT
    assert tokens[1].type == TokenType.IDENTIFIER
    assert tokens[1].value == "x"
    assert tokens[2].type == TokenType.ASSIGN
    assert tokens[3].type == TokenType.INTEGER_LITERAL
    assert tokens[3].value == "5"
    assert tokens[4].type == TokenType.SEMICOLON
    assert tokens[5].type == TokenType.EOF
    
    print("  ✓ Basic tokenization works")
    
    # Test operators
    source = "a == b && c != d"
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    
    assert tokens[1].type == TokenType.EQUAL
    assert tokens[3].type == TokenType.LOGICAL_AND
    assert tokens[5].type == TokenType.NOT_EQUAL
    
    print("  ✓ Operator tokenization works")
    
    # Test comments
    source = "// comment\nint x; /* multi\nline */"
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    
    # Should skip comments
    assert tokens[0].type == TokenType.INT
    assert tokens[1].type == TokenType.IDENTIFIER
    
    print("  ✓ Comment handling works")
    print("✅ Stage 1 tests passed!\n")


def test_parser():
    """Test syntax analysis"""
    print("Testing Stage 2: Syntax Analysis...")
    
    # Test simple function
    source = """
    int add(int a, int b) {
        return a + b;
    }
    """
    
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    assert len(ast.declarations) == 1
    assert ast.declarations[0].name == "add"
    assert len(ast.declarations[0].parameters) == 2
    
    print("  ✓ Function parsing works")
    
    # Test if statement
    source = """
    int main() {
        if (x > 0) {
            return 1;
        }
        return 0;
    }
    """
    
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    print("  ✓ If statement parsing works")
    
    # Test expressions
    source = """
    int main() {
        int x;
        x = (a + b) * c;
        return x;
    }
    """
    
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    print("  ✓ Expression parsing works")
    print("✅ Stage 2 tests passed!\n")


def test_semantic_analyzer():
    """Test semantic analysis"""
    print("Testing Stage 3: Semantic Analysis...")
    
    # Test valid program
    source = """
    int factorial(int n) {
        if (n <= 1) {
            return 1;
        }
        return n;
    }
    
    int main() {
        int x;
        x = 5;
        return x;
    }
    """
    
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    analyzer = SemanticAnalyzer()
    try:
        analyzer.analyze(ast)
        print("  ✓ Valid program analysis works")
    except SemanticError:
        print("  ✗ Valid program incorrectly rejected")
        raise
    
    # Test undefined variable
    source = """
    int main() {
        return undefined_var;
    }
    """
    
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    analyzer = SemanticAnalyzer()
    try:
        analyzer.analyze(ast)
        print("  ✗ Undefined variable not detected")
    except SemanticError:
        print("  ✓ Undefined variable detection works")
    
    print("✅ Stage 3 tests passed!\n")


def test_intermediate_code():
    """Test intermediate code generation"""
    print("Testing Stage 4: Intermediate Code Generation...")
    
    source = """
    int main() {
        int x;
        x = 5;
        return x + 1;
    }
    """
    
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    code_gen = IntermediateCodeGenerator()
    code_gen.generate(ast)
    
    # Check that TAC instructions were generated
    assert len(code_gen.instructions) > 0
    
    # Check for function start/end
    assert any("main" in str(inst) for inst in code_gen.instructions)
    
    print("  ✓ TAC generation works")
    print("✅ Stage 4 tests passed!\n")


def test_code_generator():
    """Test code generation"""
    print("Testing Stage 5: Code Generation...")
    
    source = """
    int main() {
        int x;
        x = 5;
        return x;
    }
    """
    
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    tac_gen = IntermediateCodeGenerator()
    tac_gen.generate(ast)
    
    code_gen = CodeGenerator(tac_gen.instructions)
    code_gen.generate()
    
    # Check that assembly code was generated
    assert len(code_gen.assembly_code) > 0
    
    # Check for function prologue/epilogue
    assert any("main:" in line for line in code_gen.assembly_code)
    assert any("PUSH BP" in line for line in code_gen.assembly_code)
    assert any("RET" in line for line in code_gen.assembly_code)
    
    print("  ✓ Assembly generation works")
    
    # Test optimization
    code_gen.optimize()
    
    print("  ✓ Optimization works")
    print("✅ Stage 5 tests passed!\n")


def test_full_compilation():
    """Test full compilation pipeline"""
    print("Testing Full Compilation Pipeline...")
    
    test_programs = [
        # Simple arithmetic
        """
        int main() {
            int a;
            int b;
            a = 10;
            b = 20;
            return a + b;
        }
        """,
        
        # Function with recursion
        """
        int factorial(int n) {
            if (n <= 1) {
                return 1;
            }
            return n * factorial(n - 1);
        }
        
        int main() {
            return factorial(5);
        }
        """,
        
        # Loop
        """
        int main() {
            int i;
            int sum;
            sum = 0;
            i = 0;
            while (i < 10) {
                sum = sum + i;
                i = i + 1;
            }
            return sum;
        }
        """,
    ]
    
    for i, source in enumerate(test_programs):
        try:
            # Lexer
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            
            # Parser
            parser = Parser(tokens)
            ast = parser.parse()
            
            # Semantic Analysis
            analyzer = SemanticAnalyzer()
            analyzer.analyze(ast)
            
            # Intermediate Code Generation
            tac_gen = IntermediateCodeGenerator()
            tac_gen.generate(ast)
            
            # Code Generation
            code_gen = CodeGenerator(tac_gen.instructions)
            code_gen.generate()
            code_gen.optimize()
            
            print(f"  ✓ Test program {i+1} compiled successfully")
            
        except Exception as e:
            print(f"  ✗ Test program {i+1} failed: {e}")
            raise
    
    print("✅ Full compilation tests passed!\n")


def main():
    """Run all tests"""
    print("=" * 60)
    print(" C COMPILER TEST SUITE")
    print("=" * 60)
    print()
    
    try:
        test_lexer()
        test_parser()
        test_semantic_analyzer()
        test_intermediate_code()
        test_code_generator()
        test_full_compilation()
        
        print("=" * 60)
        print(" ✅ ALL TESTS PASSED!")
        print("=" * 60)
        return 0
        
    except Exception as e:
        print()
        print("=" * 60)
        print(" ❌ TESTS FAILED!")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
