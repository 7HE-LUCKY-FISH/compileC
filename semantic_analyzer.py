"""
Semantic Analysis (Stage 3)
Performs semantic checks and builds symbol tables.
"""

from typing import Dict, List, Optional, Set
from parser import (
    ASTNode, Program, FunctionDecl, VarDecl, Parameter, CompoundStmt,
    ExpressionStmt, ReturnStmt, IfStmt, WhileStmt, ForStmt,
    Expression, BinaryOp, UnaryOp, Assignment, FunctionCall,
    Identifier, IntLiteral, FloatLiteral, StringLiteral
)


class Symbol:
    """Represents a symbol in the symbol table"""
    def __init__(self, name: str, symbol_type: str, scope: str):
        self.name = name
        self.type = symbol_type
        self.scope = scope


class SymbolTable:
    """Symbol table for tracking variables and functions"""
    def __init__(self):
        self.scopes: List[Dict[str, Symbol]] = [{}]  # Stack of scopes
        self.current_scope = "global"
    
    def enter_scope(self, scope_name: str):
        """Enter a new scope"""
        self.scopes.append({})
        self.current_scope = scope_name
    
    def exit_scope(self):
        """Exit current scope"""
        if len(self.scopes) > 1:
            self.scopes.pop()
            self.current_scope = "outer"
    
    def declare(self, name: str, symbol_type: str):
        """Declare a new symbol in the current scope"""
        if name in self.scopes[-1]:
            raise SemanticError(f"Variable '{name}' already declared in this scope")
        self.scopes[-1][name] = Symbol(name, symbol_type, self.current_scope)
    
    def lookup(self, name: str) -> Optional[Symbol]:
        """Look up a symbol in all scopes (from innermost to outermost)"""
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None
    
    def get_all_symbols(self) -> List[Symbol]:
        """Get all symbols from all scopes"""
        symbols = []
        for scope in self.scopes:
            symbols.extend(scope.values())
        return symbols


class SemanticError(Exception):
    """Semantic analysis error"""
    pass


class SemanticAnalyzer:
    """Semantic Analyzer for C code"""
    
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.current_function_return_type: Optional[str] = None
        self.errors: List[str] = []
    
    def error(self, message: str):
        """Record a semantic error"""
        self.errors.append(message)
    
    def analyze(self, ast: Program):
        """Perform semantic analysis on the AST"""
        try:
            self.visit_program(ast)
        except SemanticError as e:
            self.error(str(e))
        
        if self.errors:
            print("\n=== STAGE 3: SEMANTIC ANALYSIS ===")
            print("Semantic Errors Found:")
            for error in self.errors:
                print(f"  - {error}")
            raise SemanticError("Semantic analysis failed")
    
    def visit_program(self, node: Program):
        """Visit program node"""
        for decl in node.declarations:
            if isinstance(decl, FunctionDecl):
                self.visit_function_decl(decl)
            elif isinstance(decl, VarDecl):
                self.visit_var_decl(decl)
    
    def visit_function_decl(self, node: FunctionDecl):
        """Visit function declaration"""
        # Declare function in global scope
        try:
            self.symbol_table.declare(node.name, f"function:{node.return_type}")
        except SemanticError as e:
            self.error(str(e))
        
        if node.body:
            # Enter function scope
            self.symbol_table.enter_scope(f"function:{node.name}")
            self.current_function_return_type = node.return_type
            
            # Add parameters to function scope
            for param in node.parameters:
                try:
                    self.symbol_table.declare(param.name, param.param_type)
                except SemanticError as e:
                    self.error(str(e))
            
            # Visit function body
            self.visit_compound_stmt(node.body)
            
            # Exit function scope
            self.symbol_table.exit_scope()
            self.current_function_return_type = None
    
    def visit_var_decl(self, node: VarDecl):
        """Visit variable declaration"""
        try:
            self.symbol_table.declare(node.name, node.var_type)
        except SemanticError as e:
            self.error(str(e))
        
        if node.initializer:
            init_type = self.visit_expression(node.initializer)
            # Type checking for initialization
            if not self.is_compatible_type(node.var_type, init_type):
                self.error(
                    f"Type mismatch in initialization of '{node.name}': "
                    f"cannot assign {init_type} to {node.var_type}"
                )
    
    def visit_compound_stmt(self, node: CompoundStmt):
        """Visit compound statement"""
        for stmt in node.statements:
            self.visit_statement(stmt)
    
    def visit_statement(self, node):
        """Visit a statement"""
        if isinstance(node, VarDecl):
            self.visit_var_decl(node)
        elif isinstance(node, CompoundStmt):
            self.symbol_table.enter_scope("block")
            self.visit_compound_stmt(node)
            self.symbol_table.exit_scope()
        elif isinstance(node, ExpressionStmt):
            if node.expression:
                self.visit_expression(node.expression)
        elif isinstance(node, ReturnStmt):
            self.visit_return_stmt(node)
        elif isinstance(node, IfStmt):
            self.visit_if_stmt(node)
        elif isinstance(node, WhileStmt):
            self.visit_while_stmt(node)
        elif isinstance(node, ForStmt):
            self.visit_for_stmt(node)
    
    def visit_return_stmt(self, node: ReturnStmt):
        """Visit return statement"""
        if self.current_function_return_type is None:
            self.error("Return statement outside of function")
            return
        
        if node.expression:
            expr_type = self.visit_expression(node.expression)
            if not self.is_compatible_type(self.current_function_return_type, expr_type):
                self.error(
                    f"Return type mismatch: expected {self.current_function_return_type}, "
                    f"got {expr_type}"
                )
        elif self.current_function_return_type != "void":
            self.error(
                f"Return statement must return a value of type "
                f"{self.current_function_return_type}"
            )
    
    def visit_if_stmt(self, node: IfStmt):
        """Visit if statement"""
        self.visit_expression(node.condition)
        self.visit_statement(node.then_stmt)
        if node.else_stmt:
            self.visit_statement(node.else_stmt)
    
    def visit_while_stmt(self, node: WhileStmt):
        """Visit while statement"""
        self.visit_expression(node.condition)
        self.visit_statement(node.body)
    
    def visit_for_stmt(self, node: ForStmt):
        """Visit for statement"""
        self.symbol_table.enter_scope("for")
        
        if node.init:
            if isinstance(node.init, VarDecl):
                self.visit_var_decl(node.init)
            else:
                self.visit_statement(node.init)
        
        if node.condition:
            self.visit_expression(node.condition)
        
        if node.update:
            self.visit_expression(node.update)
        
        self.visit_statement(node.body)
        
        self.symbol_table.exit_scope()
    
    def visit_expression(self, node: Expression) -> str:
        """Visit an expression and return its type"""
        if isinstance(node, IntLiteral):
            return "int"
        elif isinstance(node, FloatLiteral):
            return "float"
        elif isinstance(node, StringLiteral):
            return "char*"
        elif isinstance(node, Identifier):
            symbol = self.symbol_table.lookup(node.name)
            if symbol is None:
                self.error(f"Undefined variable: '{node.name}'")
                return "unknown"
            return symbol.type
        elif isinstance(node, BinaryOp):
            return self.visit_binary_op(node)
        elif isinstance(node, UnaryOp):
            return self.visit_unary_op(node)
        elif isinstance(node, Assignment):
            return self.visit_assignment(node)
        elif isinstance(node, FunctionCall):
            return self.visit_function_call(node)
        else:
            return "unknown"
    
    def visit_binary_op(self, node: BinaryOp) -> str:
        """Visit binary operation"""
        left_type = self.visit_expression(node.left)
        right_type = self.visit_expression(node.right)
        
        # Logical operators return int (boolean)
        if node.operator in ['&&', '||', '==', '!=', '<', '>', '<=', '>=']:
            return "int"
        
        # Arithmetic operators - type promotion
        if node.operator in ['+', '-', '*', '/', '%']:
            if left_type == "float" or right_type == "float":
                return "float"
            return "int"
        
        return "int"
    
    def visit_unary_op(self, node: UnaryOp) -> str:
        """Visit unary operation"""
        operand_type = self.visit_expression(node.operand)
        
        if node.operator == '!':
            return "int"
        elif node.operator == '-':
            return operand_type
        
        return operand_type
    
    def visit_assignment(self, node: Assignment) -> str:
        """Visit assignment"""
        symbol = self.symbol_table.lookup(node.target)
        if symbol is None:
            self.error(f"Assignment to undefined variable: '{node.target}'")
            return "unknown"
        
        value_type = self.visit_expression(node.value)
        
        if not self.is_compatible_type(symbol.type, value_type):
            self.error(
                f"Type mismatch in assignment to '{node.target}': "
                f"cannot assign {value_type} to {symbol.type}"
            )
        
        return symbol.type
    
    def visit_function_call(self, node: FunctionCall) -> str:
        """Visit function call"""
        symbol = self.symbol_table.lookup(node.name)
        if symbol is None:
            self.error(f"Call to undefined function: '{node.name}'")
            return "unknown"
        
        if not symbol.type.startswith("function:"):
            self.error(f"'{node.name}' is not a function")
            return "unknown"
        
        # Extract return type from function type
        return_type = symbol.type.split(":", 1)[1]
        
        # Visit arguments
        for arg in node.arguments:
            self.visit_expression(arg)
        
        return return_type
    
    def is_compatible_type(self, target_type: str, source_type: str) -> bool:
        """Check if types are compatible for assignment"""
        if target_type == source_type:
            return True
        
        # Allow numeric type conversions
        if target_type in ["int", "float"] and source_type in ["int", "float"]:
            return True
        
        # Allow unknown type (error already reported)
        if source_type == "unknown":
            return True
        
        return False
    
    def print_symbol_table(self):
        """Print symbol table"""
        print("\n=== STAGE 3: SEMANTIC ANALYSIS ===")
        print("Symbol Table:")
        print(f"{'Name':<20} {'Type':<20} {'Scope':<20}")
        print("-" * 60)
        for symbol in self.symbol_table.get_all_symbols():
            print(f"{symbol.name:<20} {symbol.type:<20} {symbol.scope:<20}")
