"""
Syntax Analysis (Stage 2)
Parses tokens into an Abstract Syntax Tree (AST).
"""

from dataclasses import dataclass
from typing import List, Optional, Union
from lexer import Token, TokenType


# AST Node Classes
@dataclass
class ASTNode:
    """Base class for all AST nodes"""
    pass


@dataclass
class Program(ASTNode):
    """Root node representing the entire program"""
    declarations: List['Declaration']


@dataclass
class Declaration(ASTNode):
    """Base class for declarations"""
    pass


@dataclass
class FunctionDecl(Declaration):
    """Function declaration"""
    return_type: str
    name: str
    parameters: List['Parameter']
    body: Optional['CompoundStmt']


@dataclass
class VarDecl(Declaration):
    """Variable declaration"""
    var_type: str
    name: str
    initializer: Optional['Expression'] = None


@dataclass
class Parameter(ASTNode):
    """Function parameter"""
    param_type: str
    name: str


@dataclass
class Statement(ASTNode):
    """Base class for statements"""
    pass


@dataclass
class CompoundStmt(Statement):
    """Compound statement (block)"""
    statements: List[Statement]


@dataclass
class ExpressionStmt(Statement):
    """Expression statement"""
    expression: Optional['Expression']


@dataclass
class ReturnStmt(Statement):
    """Return statement"""
    expression: Optional['Expression']


@dataclass
class IfStmt(Statement):
    """If statement"""
    condition: 'Expression'
    then_stmt: Statement
    else_stmt: Optional[Statement] = None


@dataclass
class WhileStmt(Statement):
    """While loop"""
    condition: 'Expression'
    body: Statement


@dataclass
class ForStmt(Statement):
    """For loop"""
    init: Optional[Union[VarDecl, ExpressionStmt]]
    condition: Optional['Expression']
    update: Optional['Expression']
    body: Statement


@dataclass
class Expression(ASTNode):
    """Base class for expressions"""
    pass


@dataclass
class BinaryOp(Expression):
    """Binary operation"""
    operator: str
    left: Expression
    right: Expression


@dataclass
class UnaryOp(Expression):
    """Unary operation"""
    operator: str
    operand: Expression


@dataclass
class Identifier(Expression):
    """Identifier"""
    name: str


@dataclass
class IntLiteral(Expression):
    """Integer literal"""
    value: int


@dataclass
class FloatLiteral(Expression):
    """Float literal"""
    value: float


@dataclass
class StringLiteral(Expression):
    """String literal"""
    value: str


@dataclass
class FunctionCall(Expression):
    """Function call"""
    name: str
    arguments: List[Expression]


@dataclass
class Assignment(Expression):
    """Assignment expression"""
    target: str
    value: Expression


class Parser:
    """Syntax Analyzer for C code"""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
        self.current_token = tokens[0] if tokens else None
    
    def error(self, message: str):
        if self.current_token:
            raise SyntaxError(
                f"Parse error at line {self.current_token.line}, "
                f"column {self.current_token.column}: {message}"
            )
        raise SyntaxError(f"Parse error: {message}")
    
    def advance(self):
        """Move to the next token"""
        if self.position < len(self.tokens) - 1:
            self.position += 1
            self.current_token = self.tokens[self.position]
    
    def expect(self, token_type: TokenType) -> Token:
        """Expect a specific token type and consume it"""
        if self.current_token.type != token_type:
            self.error(f"Expected {token_type.name}, got {self.current_token.type.name}")
        token = self.current_token
        self.advance()
        return token
    
    def match(self, *token_types: TokenType) -> bool:
        """Check if current token matches any of the given types"""
        return self.current_token.type in token_types
    
    def parse(self) -> Program:
        """Parse the token stream into an AST"""
        declarations = []
        
        while self.current_token.type != TokenType.EOF:
            declarations.append(self.parse_declaration())
        
        return Program(declarations)
    
    def parse_declaration(self) -> Declaration:
        """Parse a declaration (function or variable)"""
        # Get type
        type_token = self.current_token
        if not self.match(TokenType.INT, TokenType.FLOAT, TokenType.CHAR, TokenType.VOID):
            self.error(f"Expected type specifier, got {self.current_token.type.name}")
        
        var_type = type_token.value
        self.advance()
        
        # Get name
        name_token = self.expect(TokenType.IDENTIFIER)
        name = name_token.value
        
        # Check if it's a function
        if self.current_token.type == TokenType.LPAREN:
            return self.parse_function_declaration(var_type, name)
        else:
            return self.parse_variable_declaration(var_type, name)
    
    def parse_function_declaration(self, return_type: str, name: str) -> FunctionDecl:
        """Parse function declaration"""
        self.expect(TokenType.LPAREN)
        
        # Parse parameters
        parameters = []
        if self.current_token.type != TokenType.RPAREN:
            parameters = self.parse_parameter_list()
        
        self.expect(TokenType.RPAREN)
        
        # Check for function body or just declaration
        body = None
        if self.current_token.type == TokenType.LBRACE:
            body = self.parse_compound_statement()
        else:
            self.expect(TokenType.SEMICOLON)
        
        return FunctionDecl(return_type, name, parameters, body)
    
    def parse_parameter_list(self) -> List[Parameter]:
        """Parse function parameter list"""
        parameters = []
        
        while True:
            # Get parameter type
            if not self.match(TokenType.INT, TokenType.FLOAT, TokenType.CHAR):
                self.error("Expected parameter type")
            
            param_type = self.current_token.value
            self.advance()
            
            # Get parameter name
            param_name = self.expect(TokenType.IDENTIFIER).value
            
            parameters.append(Parameter(param_type, param_name))
            
            if self.current_token.type != TokenType.COMMA:
                break
            self.advance()  # Skip comma
        
        return parameters
    
    def parse_variable_declaration(self, var_type: str, name: str) -> VarDecl:
        """Parse variable declaration"""
        initializer = None
        
        if self.current_token.type == TokenType.ASSIGN:
            self.advance()  # Skip =
            initializer = self.parse_expression()
        
        self.expect(TokenType.SEMICOLON)
        
        return VarDecl(var_type, name, initializer)
    
    def parse_compound_statement(self) -> CompoundStmt:
        """Parse compound statement (block)"""
        self.expect(TokenType.LBRACE)
        
        statements = []
        while self.current_token.type != TokenType.RBRACE:
            statements.append(self.parse_statement())
        
        self.expect(TokenType.RBRACE)
        
        return CompoundStmt(statements)
    
    def parse_statement(self) -> Statement:
        """Parse a statement"""
        # Check for declarations
        if self.match(TokenType.INT, TokenType.FLOAT, TokenType.CHAR):
            return self.parse_declaration()
        
        # Return statement
        if self.current_token.type == TokenType.RETURN:
            return self.parse_return_statement()
        
        # If statement
        if self.current_token.type == TokenType.IF:
            return self.parse_if_statement()
        
        # While statement
        if self.current_token.type == TokenType.WHILE:
            return self.parse_while_statement()
        
        # For statement
        if self.current_token.type == TokenType.FOR:
            return self.parse_for_statement()
        
        # Compound statement
        if self.current_token.type == TokenType.LBRACE:
            return self.parse_compound_statement()
        
        # Expression statement
        return self.parse_expression_statement()
    
    def parse_return_statement(self) -> ReturnStmt:
        """Parse return statement"""
        self.expect(TokenType.RETURN)
        
        expression = None
        if self.current_token.type != TokenType.SEMICOLON:
            expression = self.parse_expression()
        
        self.expect(TokenType.SEMICOLON)
        
        return ReturnStmt(expression)
    
    def parse_if_statement(self) -> IfStmt:
        """Parse if statement"""
        self.expect(TokenType.IF)
        self.expect(TokenType.LPAREN)
        condition = self.parse_expression()
        self.expect(TokenType.RPAREN)
        
        then_stmt = self.parse_statement()
        
        else_stmt = None
        if self.current_token.type == TokenType.ELSE:
            self.advance()
            else_stmt = self.parse_statement()
        
        return IfStmt(condition, then_stmt, else_stmt)
    
    def parse_while_statement(self) -> WhileStmt:
        """Parse while statement"""
        self.expect(TokenType.WHILE)
        self.expect(TokenType.LPAREN)
        condition = self.parse_expression()
        self.expect(TokenType.RPAREN)
        
        body = self.parse_statement()
        
        return WhileStmt(condition, body)
    
    def parse_for_statement(self) -> ForStmt:
        """Parse for statement"""
        self.expect(TokenType.FOR)
        self.expect(TokenType.LPAREN)
        
        # Init
        init = None
        if self.match(TokenType.INT, TokenType.FLOAT, TokenType.CHAR):
            init = self.parse_declaration()
        elif self.current_token.type != TokenType.SEMICOLON:
            init = self.parse_expression_statement()
        else:
            self.advance()  # Skip semicolon
        
        # Condition
        condition = None
        if self.current_token.type != TokenType.SEMICOLON:
            condition = self.parse_expression()
        self.expect(TokenType.SEMICOLON)
        
        # Update
        update = None
        if self.current_token.type != TokenType.RPAREN:
            update = self.parse_expression()
        self.expect(TokenType.RPAREN)
        
        body = self.parse_statement()
        
        return ForStmt(init, condition, update, body)
    
    def parse_expression_statement(self) -> ExpressionStmt:
        """Parse expression statement"""
        if self.current_token.type == TokenType.SEMICOLON:
            self.advance()
            return ExpressionStmt(None)
        
        expression = self.parse_expression()
        self.expect(TokenType.SEMICOLON)
        
        return ExpressionStmt(expression)
    
    def parse_expression(self) -> Expression:
        """Parse expression (assignment or logical OR)"""
        expr = self.parse_logical_or()
        
        # Check for assignment
        if self.current_token.type == TokenType.ASSIGN:
            if not isinstance(expr, Identifier):
                self.error("Invalid assignment target")
            self.advance()  # Skip =
            value = self.parse_expression()
            return Assignment(expr.name, value)
        
        return expr
    
    def parse_logical_or(self) -> Expression:
        """Parse logical OR expression"""
        left = self.parse_logical_and()
        
        while self.current_token.type == TokenType.LOGICAL_OR:
            op = self.current_token.value
            self.advance()
            right = self.parse_logical_and()
            left = BinaryOp(op, left, right)
        
        return left
    
    def parse_logical_and(self) -> Expression:
        """Parse logical AND expression"""
        left = self.parse_equality()
        
        while self.current_token.type == TokenType.LOGICAL_AND:
            op = self.current_token.value
            self.advance()
            right = self.parse_equality()
            left = BinaryOp(op, left, right)
        
        return left
    
    def parse_equality(self) -> Expression:
        """Parse equality expression"""
        left = self.parse_relational()
        
        while self.match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            op = self.current_token.value
            self.advance()
            right = self.parse_relational()
            left = BinaryOp(op, left, right)
        
        return left
    
    def parse_relational(self) -> Expression:
        """Parse relational expression"""
        left = self.parse_additive()
        
        while self.match(TokenType.LESS_THAN, TokenType.GREATER_THAN, 
                         TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL):
            op = self.current_token.value
            self.advance()
            right = self.parse_additive()
            left = BinaryOp(op, left, right)
        
        return left
    
    def parse_additive(self) -> Expression:
        """Parse additive expression"""
        left = self.parse_multiplicative()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op = self.current_token.value
            self.advance()
            right = self.parse_multiplicative()
            left = BinaryOp(op, left, right)
        
        return left
    
    def parse_multiplicative(self) -> Expression:
        """Parse multiplicative expression"""
        left = self.parse_unary()
        
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            op = self.current_token.value
            self.advance()
            right = self.parse_unary()
            left = BinaryOp(op, left, right)
        
        return left
    
    def parse_unary(self) -> Expression:
        """Parse unary expression"""
        if self.match(TokenType.MINUS, TokenType.LOGICAL_NOT):
            op = self.current_token.value
            self.advance()
            operand = self.parse_unary()
            return UnaryOp(op, operand)
        
        return self.parse_postfix()
    
    def parse_postfix(self) -> Expression:
        """Parse postfix expression"""
        expr = self.parse_primary()
        
        # Function call
        if self.current_token.type == TokenType.LPAREN:
            if not isinstance(expr, Identifier):
                self.error("Invalid function call")
            self.advance()  # Skip (
            
            arguments = []
            if self.current_token.type != TokenType.RPAREN:
                arguments.append(self.parse_expression())
                while self.current_token.type == TokenType.COMMA:
                    self.advance()  # Skip comma
                    arguments.append(self.parse_expression())
            
            self.expect(TokenType.RPAREN)
            expr = FunctionCall(expr.name, arguments)
        
        return expr
    
    def parse_primary(self) -> Expression:
        """Parse primary expression"""
        # Integer literal
        if self.current_token.type == TokenType.INTEGER_LITERAL:
            value = int(self.current_token.value)
            self.advance()
            return IntLiteral(value)
        
        # Float literal
        if self.current_token.type == TokenType.FLOAT_LITERAL:
            value = float(self.current_token.value)
            self.advance()
            return FloatLiteral(value)
        
        # String literal
        if self.current_token.type == TokenType.STRING_LITERAL:
            value = self.current_token.value
            self.advance()
            return StringLiteral(value)
        
        # Identifier
        if self.current_token.type == TokenType.IDENTIFIER:
            name = self.current_token.value
            self.advance()
            return Identifier(name)
        
        # Parenthesized expression
        if self.current_token.type == TokenType.LPAREN:
            self.advance()  # Skip (
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr
        
        self.error(f"Unexpected token: {self.current_token.type.name}")
    
    def print_ast(self, node: ASTNode, indent: int = 0):
        """Print AST for debugging"""
        prefix = "  " * indent
        if isinstance(node, Program):
            print(f"{prefix}Program")
            for decl in node.declarations:
                self.print_ast(decl, indent + 1)
        elif isinstance(node, FunctionDecl):
            print(f"{prefix}FunctionDecl: {node.return_type} {node.name}")
            print(f"{prefix}  Parameters:")
            for param in node.parameters:
                self.print_ast(param, indent + 2)
            if node.body:
                print(f"{prefix}  Body:")
                self.print_ast(node.body, indent + 2)
        elif isinstance(node, Parameter):
            print(f"{prefix}Parameter: {node.param_type} {node.name}")
        elif isinstance(node, VarDecl):
            print(f"{prefix}VarDecl: {node.var_type} {node.name}")
            if node.initializer:
                print(f"{prefix}  Initializer:")
                self.print_ast(node.initializer, indent + 2)
        elif isinstance(node, CompoundStmt):
            print(f"{prefix}CompoundStmt")
            for stmt in node.statements:
                self.print_ast(stmt, indent + 1)
        elif isinstance(node, ReturnStmt):
            print(f"{prefix}ReturnStmt")
            if node.expression:
                self.print_ast(node.expression, indent + 1)
        elif isinstance(node, IfStmt):
            print(f"{prefix}IfStmt")
            print(f"{prefix}  Condition:")
            self.print_ast(node.condition, indent + 2)
            print(f"{prefix}  Then:")
            self.print_ast(node.then_stmt, indent + 2)
            if node.else_stmt:
                print(f"{prefix}  Else:")
                self.print_ast(node.else_stmt, indent + 2)
        elif isinstance(node, WhileStmt):
            print(f"{prefix}WhileStmt")
            print(f"{prefix}  Condition:")
            self.print_ast(node.condition, indent + 2)
            print(f"{prefix}  Body:")
            self.print_ast(node.body, indent + 2)
        elif isinstance(node, ForStmt):
            print(f"{prefix}ForStmt")
            if node.init:
                print(f"{prefix}  Init:")
                self.print_ast(node.init, indent + 2)
            if node.condition:
                print(f"{prefix}  Condition:")
                self.print_ast(node.condition, indent + 2)
            if node.update:
                print(f"{prefix}  Update:")
                self.print_ast(node.update, indent + 2)
            print(f"{prefix}  Body:")
            self.print_ast(node.body, indent + 2)
        elif isinstance(node, ExpressionStmt):
            print(f"{prefix}ExpressionStmt")
            if node.expression:
                self.print_ast(node.expression, indent + 1)
        elif isinstance(node, BinaryOp):
            print(f"{prefix}BinaryOp: {node.operator}")
            self.print_ast(node.left, indent + 1)
            self.print_ast(node.right, indent + 1)
        elif isinstance(node, UnaryOp):
            print(f"{prefix}UnaryOp: {node.operator}")
            self.print_ast(node.operand, indent + 1)
        elif isinstance(node, Assignment):
            print(f"{prefix}Assignment: {node.target}")
            self.print_ast(node.value, indent + 1)
        elif isinstance(node, FunctionCall):
            print(f"{prefix}FunctionCall: {node.name}")
            for arg in node.arguments:
                self.print_ast(arg, indent + 1)
        elif isinstance(node, Identifier):
            print(f"{prefix}Identifier: {node.name}")
        elif isinstance(node, IntLiteral):
            print(f"{prefix}IntLiteral: {node.value}")
        elif isinstance(node, FloatLiteral):
            print(f"{prefix}FloatLiteral: {node.value}")
        elif isinstance(node, StringLiteral):
            print(f"{prefix}StringLiteral: \"{node.value}\"")
