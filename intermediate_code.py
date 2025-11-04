"""
Intermediate Code Generation (Stage 4)
Generates three-address code (TAC) intermediate representation.
"""

from typing import List, Optional
from parser import (
    ASTNode, Program, FunctionDecl, VarDecl, Parameter, CompoundStmt,
    ExpressionStmt, ReturnStmt, IfStmt, WhileStmt, ForStmt,
    Expression, BinaryOp, UnaryOp, Assignment, FunctionCall,
    Identifier, IntLiteral, FloatLiteral, StringLiteral
)


class TACInstruction:
    """Three-Address Code instruction"""
    pass


class TACAssign(TACInstruction):
    """TAC assignment: result = arg1"""
    def __init__(self, result: str, arg1: str):
        self.result = result
        self.arg1 = arg1
    
    def __str__(self):
        return f"{self.result} = {self.arg1}"


class TACBinaryOp(TACInstruction):
    """TAC binary operation: result = arg1 op arg2"""
    def __init__(self, result: str, arg1: str, op: str, arg2: str):
        self.result = result
        self.arg1 = arg1
        self.op = op
        self.arg2 = arg2
    
    def __str__(self):
        return f"{self.result} = {self.arg1} {self.op} {self.arg2}"


class TACUnaryOp(TACInstruction):
    """TAC unary operation: result = op arg"""
    def __init__(self, result: str, op: str, arg: str):
        self.result = result
        self.op = op
        self.arg = arg
    
    def __str__(self):
        return f"{self.result} = {self.op} {self.arg}"


class TACLabel(TACInstruction):
    """TAC label: label:"""
    def __init__(self, label: str):
        self.label = label
    
    def __str__(self):
        return f"{self.label}:"


class TACGoto(TACInstruction):
    """TAC unconditional jump: goto label"""
    def __init__(self, label: str):
        self.label = label
    
    def __str__(self):
        return f"goto {self.label}"


class TACIfGoto(TACInstruction):
    """TAC conditional jump: if condition goto label"""
    def __init__(self, condition: str, label: str):
        self.condition = condition
        self.label = label
    
    def __str__(self):
        return f"if {self.condition} goto {self.label}"


class TACIfFalseGoto(TACInstruction):
    """TAC conditional jump: ifFalse condition goto label"""
    def __init__(self, condition: str, label: str):
        self.condition = condition
        self.label = label
    
    def __str__(self):
        return f"ifFalse {self.condition} goto {self.label}"


class TACCall(TACInstruction):
    """TAC function call: result = call function, n_args"""
    def __init__(self, result: Optional[str], function: str, n_args: int):
        self.result = result
        self.function = function
        self.n_args = n_args
    
    def __str__(self):
        if self.result:
            return f"{self.result} = call {self.function}, {self.n_args}"
        return f"call {self.function}, {self.n_args}"


class TACParam(TACInstruction):
    """TAC parameter: param arg"""
    def __init__(self, arg: str):
        self.arg = arg
    
    def __str__(self):
        return f"param {self.arg}"


class TACReturn(TACInstruction):
    """TAC return: return [value]"""
    def __init__(self, value: Optional[str] = None):
        self.value = value
    
    def __str__(self):
        if self.value:
            return f"return {self.value}"
        return "return"


class TACFunctionStart(TACInstruction):
    """TAC function start: function name:"""
    def __init__(self, name: str):
        self.name = name
    
    def __str__(self):
        return f"function {self.name}:"


class TACFunctionEnd(TACInstruction):
    """TAC function end: end function"""
    def __init__(self, name: str):
        self.name = name
    
    def __str__(self):
        return f"end function {self.name}"


class IntermediateCodeGenerator:
    """Generates three-address code (TAC) from AST"""
    
    def __init__(self):
        self.instructions: List[TACInstruction] = []
        self.temp_counter = 0
        self.label_counter = 0
    
    def new_temp(self) -> str:
        """Generate a new temporary variable"""
        temp = f"t{self.temp_counter}"
        self.temp_counter += 1
        return temp
    
    def new_label(self) -> str:
        """Generate a new label"""
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label
    
    def emit(self, instruction: TACInstruction):
        """Emit a TAC instruction"""
        self.instructions.append(instruction)
    
    def generate(self, ast: Program):
        """Generate intermediate code from AST"""
        self.visit_program(ast)
    
    def visit_program(self, node: Program):
        """Visit program node"""
        for decl in node.declarations:
            if isinstance(decl, FunctionDecl):
                self.visit_function_decl(decl)
            elif isinstance(decl, VarDecl):
                self.visit_var_decl(decl)
    
    def visit_function_decl(self, node: FunctionDecl):
        """Visit function declaration"""
        if node.body:
            self.emit(TACFunctionStart(node.name))
            self.visit_compound_stmt(node.body)
            self.emit(TACFunctionEnd(node.name))
    
    def visit_var_decl(self, node: VarDecl):
        """Visit variable declaration"""
        if node.initializer:
            temp = self.visit_expression(node.initializer)
            self.emit(TACAssign(node.name, temp))
    
    def visit_compound_stmt(self, node: CompoundStmt):
        """Visit compound statement"""
        for stmt in node.statements:
            self.visit_statement(stmt)
    
    def visit_statement(self, node):
        """Visit a statement"""
        if isinstance(node, VarDecl):
            self.visit_var_decl(node)
        elif isinstance(node, CompoundStmt):
            self.visit_compound_stmt(node)
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
        if node.expression:
            temp = self.visit_expression(node.expression)
            self.emit(TACReturn(temp))
        else:
            self.emit(TACReturn())
    
    def visit_if_stmt(self, node: IfStmt):
        """Visit if statement"""
        condition_temp = self.visit_expression(node.condition)
        
        if node.else_stmt:
            # if-else statement
            else_label = self.new_label()
            end_label = self.new_label()
            
            self.emit(TACIfFalseGoto(condition_temp, else_label))
            self.visit_statement(node.then_stmt)
            self.emit(TACGoto(end_label))
            self.emit(TACLabel(else_label))
            self.visit_statement(node.else_stmt)
            self.emit(TACLabel(end_label))
        else:
            # if statement without else
            end_label = self.new_label()
            self.emit(TACIfFalseGoto(condition_temp, end_label))
            self.visit_statement(node.then_stmt)
            self.emit(TACLabel(end_label))
    
    def visit_while_stmt(self, node: WhileStmt):
        """Visit while statement"""
        start_label = self.new_label()
        end_label = self.new_label()
        
        self.emit(TACLabel(start_label))
        condition_temp = self.visit_expression(node.condition)
        self.emit(TACIfFalseGoto(condition_temp, end_label))
        self.visit_statement(node.body)
        self.emit(TACGoto(start_label))
        self.emit(TACLabel(end_label))
    
    def visit_for_stmt(self, node: ForStmt):
        """Visit for statement"""
        # Init
        if node.init:
            if isinstance(node.init, VarDecl):
                self.visit_var_decl(node.init)
            else:
                self.visit_statement(node.init)
        
        start_label = self.new_label()
        end_label = self.new_label()
        update_label = self.new_label()
        
        # Condition check
        self.emit(TACLabel(start_label))
        if node.condition:
            condition_temp = self.visit_expression(node.condition)
            self.emit(TACIfFalseGoto(condition_temp, end_label))
        
        # Body
        self.visit_statement(node.body)
        
        # Update
        self.emit(TACLabel(update_label))
        if node.update:
            self.visit_expression(node.update)
        
        self.emit(TACGoto(start_label))
        self.emit(TACLabel(end_label))
    
    def visit_expression(self, node: Expression) -> str:
        """Visit an expression and return the temporary holding its result"""
        if isinstance(node, IntLiteral):
            return str(node.value)
        elif isinstance(node, FloatLiteral):
            return str(node.value)
        elif isinstance(node, StringLiteral):
            return f'"{node.value}"'
        elif isinstance(node, Identifier):
            return node.name
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
        left_temp = self.visit_expression(node.left)
        right_temp = self.visit_expression(node.right)
        
        result_temp = self.new_temp()
        self.emit(TACBinaryOp(result_temp, left_temp, node.operator, right_temp))
        
        return result_temp
    
    def visit_unary_op(self, node: UnaryOp) -> str:
        """Visit unary operation"""
        operand_temp = self.visit_expression(node.operand)
        
        result_temp = self.new_temp()
        self.emit(TACUnaryOp(result_temp, node.operator, operand_temp))
        
        return result_temp
    
    def visit_assignment(self, node: Assignment) -> str:
        """Visit assignment"""
        value_temp = self.visit_expression(node.value)
        self.emit(TACAssign(node.target, value_temp))
        return node.target
    
    def visit_function_call(self, node: FunctionCall) -> str:
        """Visit function call"""
        # Emit parameters in reverse order (common convention)
        for arg in reversed(node.arguments):
            arg_temp = self.visit_expression(arg)
            self.emit(TACParam(arg_temp))
        
        result_temp = self.new_temp()
        self.emit(TACCall(result_temp, node.name, len(node.arguments)))
        
        return result_temp
    
    def print_tac(self):
        """Print three-address code"""
        print("\n=== STAGE 4: INTERMEDIATE CODE GENERATION ===")
        print("Three-Address Code (TAC):")
        print("-" * 60)
        for instruction in self.instructions:
            print(f"  {instruction}")
