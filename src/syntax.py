from typing import *
from lexer import LexicalAnalyzer
from errors import CompilationError
from token import Token
from errors import CompilerSyntaxError

class SyntaxTree:
    EXPRESSION = 0
    IDENTIFIER = 1
    NUMERIC_LITERAL = 2
    WHILE_STATEMENT = 3
    FOR_STATEMENT = 4
    BLOCK_STATEMENT = 5

    VARIABLE_DECLARATION = 6
    FUNCTION_DECLARATION = 7

    EXTERNAL_BLOCK = 8
    RETURN_STATEMENT = 9
    FUNCTION_DEFINITION = 10
    CONDITIONAL_STATEMENT = 11

    NAME = ["EXPRESSION", "IDENTIFIER", "NUMERIC_LITERAL","WHILE", "FOR", "BLOCK", "VAR_DECL", "FUNC_DECL", "EXTERNAL_BLOCK", "RETURN_STATEMENT", "FUNCTION_DEFINITION", "CONDITIONAL_STATEMENT"]

    _id = 0



    def __init__(self, typ, expression_type, line=0, token=None):
        self.children = []
        self.type = typ
        self.expression_type = expression_type
        self.value = 0
        self.line = line

        self.id = SyntaxTree._id
        SyntaxTree._id += 1

        self.data_type = None
        
        self.token = token
    
    def __str__(self):
        children_id_str = ",".join([str(i.id) if i is not None else "None" for i in self.children])
        return f"SyntaxTreeNode(id={self.id}, type={SyntaxTree.NAME[self.type]}, expression_type={str(self.expression_type)}, value={self.value}, children={children_id_str})" + ("\n" if len(self.children) > 0 else "") +  "\n".join([str(i) for i in self.children])
    
    def __repr__(self):
        return self.__str__()

class Expression(SyntaxTree):
    def __init__(self, expression_type:str, children: list, token: Token):
        super().__init__(SyntaxTree.EXPRESSION, expression_type, 0, token)
        self.expression_type = expression_type
        self.children : list[Expression] = children

class UnaryOperation(Expression):
    def __init__(self, expression_type:str, operand: Expression, token: Token):
        super().__init__(expression_type, [operand], token)
class BinaryOperation(Expression):
    def __init__(self, expression_type:str, operandL: Expression, operandR: Expression, token: Token):
        super().__init__(expression_type, [operandL, operandR], token)

class AssignmentOperation(Expression):
    def __init__(self, expression_type:str, location: Expression, value: Expression, token: Token):
        super().__init__(expression_type, [location, value], token)
    
class ArrayDereference(Expression):
    def __init__(self, pointer: Expression, index: Expression, token: Token):
        super().__init__("ARRAY_DEREFERENCE", [], token)
        self.pointer = pointer
        self.index = index

class FunctionCall(Expression):
    def __init__(self, function_name:Expression, parameters: list[Expression], token: Token):
        super().__init__("FUNCTION_CALL", [function_name] + parameters, token)
        self.function_name = function_name
        self.parameters = parameters

class Identifier(SyntaxTree):
    def __init__(self, identifier:str, token:Token):
        super().__init__(SyntaxTree.IDENTIFIER, [], 0, token)
        self.value = identifier
        self.identifier = identifier
class StructReference(Expression):
    def __init__(self, expression_type:str, operand: Expression, member: Identifier, token: Token):
        super().__init__(expression_type, [operand, member], token)

class CType:
    def __init__(self, base:str, pointer_count:int=0):
        self.base = base
        self.pointer_count = pointer_count
    
    def __str__(self):
        pointer = "*" * self.pointer_count
        return f"{self.base}{pointer}"
    
    def __repr__(self):
        return f"CType({self.__str__()})"

class CFunctionType:
    def __init__(self, return_type:CType, parameter_types:list[CType]):
        self.return_type = return_type
        self.parameter_types = parameter_types
    
class VariableDeclaration(SyntaxTree):
    def __init__(self, identifier:str, type:CType, token:Token):
        super().__init__(SyntaxTree.VARIABLE_DECLARATION, 0, 0, token)
        self.identifier = identifier
        self.declared_type = type
        
    def __str__(self):
        return f"VariableDeclaration(id={self.id}, name={self.identifier}, type={str(self.declared_type)})"
    def __repr__(self):
        return self.__str__()
            
class FunctionDeclaration(SyntaxTree):
    def __init__(self, identifier:str, return_type:CType, parameters:list[CType], token:Token):
        super().__init__(SyntaxTree.FUNCTION_DECLARATION, 0, 0, token)
        self.identifier = identifier
        self.return_type = return_type
        self.parameters = parameters
        self.function_type = CFunctionType(return_type, parameters)
    
    def __str__(self):
        parameters_str = ", ".join([str(param) for param in self.parameters])   
        return f"FunctionDeclaration(id={self.id}, name={self.identifier}, parameters=[{parameters_str}], return_type={str(self.return_type)})"
    def __repr__(self):
        return self.__str__()
    
class FunctionDefinition(SyntaxTree):
    def __init__(self, identifier:str, return_type:CType, parameters:list[tuple[str, CType]], body:SyntaxTree, token:Token):
        super().__init__(SyntaxTree.FUNCTION_DEFINITION, 0, 0, token)
        self.identifier = identifier
        self.return_type = return_type
        self.parameters = parameters
        self.body = body
        self.function_type = CFunctionType(return_type, parameters)

    def __str__(self):
        parameters_str = ", ".join([f"{name}:{str(typ)}" for name, typ in self.parameters])   
        return f"FunctionDefinition(id={self.id}, name={self.identifier}, parameters=[{parameters_str}], return_type={str(self.return_type)}, body={self.body.id})" + ("\n" + str(self.body) if self.body is not None else "")
    def __repr__(self):
        return self.__str__()
class BlockStatement(SyntaxTree):
    def __init__(self, statements:SyntaxTree, token:Token):
        super().__init__(SyntaxTree.BLOCK_STATEMENT, 0, 0, token)
        self.children = statements
    

class ExternalBlockStatement(SyntaxTree):
    def __init__(self, statements:SyntaxTree, token:Token):
        super().__init__(SyntaxTree.EXTERNAL_BLOCK, 0, 0, token)
        self.children = statements

class ReturnStatement(SyntaxTree):
    def __init__(self, expression:Expression, token:Token):
        super().__init__(SyntaxTree.RETURN_STATEMENT, 0, 0, token)
        self.children = [expression]

class WhileStatement(SyntaxTree):
    def __init__(self, condition:Expression, body:SyntaxTree, token:Token):
        super().__init__(SyntaxTree.WHILE_STATEMENT, 0, 0, token)
        self.condition = condition
        self.body = body
        self.children = [condition, body]

class ConditionalStatement(SyntaxTree):
    def __init__(self, condition:Expression, if_block:SyntaxTree, else_block:SyntaxTree | None, token:Token):
        super().__init__(SyntaxTree.CONDITIONAL_STATEMENT, 0, 0, token)
        self.condition = condition
        self.if_block = if_block
        self.else_block = else_block
        self.children = [condition, if_block]
        if else_block is not None:
            self.children.append(else_block)

class SyntaticAnalyzer:
    STATEMENT = 0
    IF_STATEMENT = 1
    ELSE_STATEMENT = 2
    ELSE_IF_STATEMENT = 3
    WHILE_STATEMENT = 3
    FOR_STATEMENT = 4
    BLOCK_STATEMENT = 5

    EXPRESSION = 104
    L_VALUE = 105
    R_VALUE = 106

    SCOPE_EXPRESSION  = 107
    POSTFIX_EXPRESSION = 108
    UNARY_EXPRESSION = 109
    POINTER_TO_MEMBER_EXPRESSION = 110
    MULTIPLICATIVE_EXPRESSION = 111
    ADDITIVE_EXPRESSION = 112
    SHIFT_EXPRESSION  = 113
    THREE_WAY_COMPARE_EXPRESSION  = 114
    RELATIONAL_COMPARE_EXPRESSION = 115
    EQUALITY_COMPARE_EXPRESSION = 116
    BITWISE_AND_EXPRESSION  = 117
    BITWISE_XOR_EXPRESSION  = 118
    BITWISE_OR_EXPRESSION  = 119
    LOGICAL_AND_EXPRESSION = 120
    LOGICAL_OR_EXPRESSION = 121
    ASSIGNMENT_EXPRESSION = 122
    COMMA_EXPRESSION = 123

    OTHER = -1

    def _is_keyword(self, i = 0, keyword : str | None = None):
        if(self.tokens[i].type != LexicalAnalyzer.KEYWORD):
            return False
        return self.tokens[i].value == keyword if keyword != None else True

    def _is_operator(self, i = 0, operator : str | None = None):
        if(self.tokens[i].type != LexicalAnalyzer.OPERATOR):
            return False
        return self.tokens[i].value == operator if operator != None else True

    def _analyze_if_self(self, i = 0):
        if(self._is_keyword(i, "if")):
            pass
    
    def _first_outside_parenthesis(self, matches: List[str], i = 0, j = -1) -> int:
        j = len(self.tokens) if j == -1 else j

        while(i < j):
            curr = self.tokens[i]
            
            if(self.parenthesis_skip_list[i] != -1):
                i = self.parenthesis_skip_list[i]
            elif(curr.value in matches):
                return i
            
            i += 1
        return -1
    
    def _last_outside_parenthesis(self, matches, i = 0, j = -1) -> int:
        j = len(self.tokens) - 1 if j == -1 else j - 1

        while(i <= j):
            curr = self.tokens[j]
            
            if(self.parenthesis_skip_list[j] != -1):
                j = self.parenthesis_skip_list[i]
            elif(curr.value in matches):
                return j
            
            j -= 1
        return -1

    def _parse_primary(self, i = 0, j = -1):
        if(i == j) :
            prev_line = self.tokens[i-1].value if i > 0 else 0
            raise CompilationError("Expected expression", prev_line)
        

        if(j - i > 1):
            if(self.tokens[i].value == "(" and self.tokens[j-1].value == ")" and self.parenthesis_skip_list[self.parenthesis_skip_list[i]] == i):
                return self._parse_expression(i + 1, j - 1)
        else:
            if(self.tokens[i].type == LexicalAnalyzer.HEX_LITERAL):
                a = SyntaxTree(SyntaxTree.NUMERIC_LITERAL, self.tokens[i].type, self.tokens[i].value)
                a.value = str(int(self.tokens[i].value[2:], base=16))
                return a
            if(self.tokens[i].type == LexicalAnalyzer.NUM_LITERAL):
                a = SyntaxTree(SyntaxTree.NUMERIC_LITERAL, self.tokens[i].type, self.tokens[i].value)
                a.value = str(int(self.tokens[i].value, base=16))
                return a

            return Identifier(self.tokens[i].value, self.tokens[i])
    
    def _parse_expression_list(self, i = 0, j = -1) -> List[Expression]:
        out = []
        while(i < j):
            
            k = self._first_outside_parenthesis(",", i, j)
            if(k == -1):
                out += [self._parse_assignment(i, j)]
                return out
            out += [self._parse_assignment(i, k)]
            i = k + 1
    
    def _parse_postfix(self, i = 0, j = -1):
        if(j - i > 1):
            operator = self.tokens[j-1].value
            if(operator in ["++", "--"]):
                return UnaryOperation(
                    operator,
                    self._parse_postfix(i, j-1),
                    self.tokens[j-1]
                )
            if(operator == "]"):
                operator_location = self.parenthesis_skip_list[j-1]
                return ArrayDereference(
                    self._parse_postfix(i, operator_location),
                    self._parse_expression(operator_location + 1, j - 1),
                    self.tokens[j-1]
                )

            if(operator == ")"):
                operator_location = self.parenthesis_skip_list[j-1]
                
                if(operator_location == i):
                    return self._parse_primary(i, j)
                    
                
                return FunctionCall(
                    self._parse_postfix(i, operator_location),
                    self._parse_expression_list(operator_location + 1, j - 1),
                    self.tokens[j-1]
                )

        if(j - i > 2):
            operator = self.tokens[j-2].value
            if(operator in ["->"] and j-2 != i):
                new_tree = SyntaxTree(SyntaxTree.EXPRESSION, operator, self.tokens[j-2].value)
                new_tree.children = [
                    self._parse_postfix(i, j-2),
                    SyntaxTree(SyntaxTree.IDENTIFIER, self.tokens[j-1])
                ]
                return new_tree

        return self._parse_primary(i, j)

    def _parse_unary(self, i = 0, j = -1):
        if(self.tokens[i].value in ["++", "--", "-", "+", "!", "~", "*", "&", "sizeof"]):
            return UnaryOperation(
                self.tokens[i].value+"_pre",
                self._parse_unary(i + 1, j),
                self.tokens[i]
            )
        
        return self._parse_postfix(i, j)
    
    # def _parse_pointer_to_member(self, i = 0, j = -1):
    #     operator_location = self._last_outside_parenthesis(["->*", ".*"], i, j)
    #     if(operator_location != -1 and operator_location != i):
    #         new_tree = SyntaxTree(SyntaxTree.EXPRESSION, self.tokens[operator_location].type)
    #         new_tree.children = [
    #             self._parse_pointer_to_member(i, operator_location),
    #             self._parse_unary(operator_location+1, j)
    #         ]
    #         return new_tree

    #     return self._parse_unary(i, j)
    def _parse_multiplicative(self, i = 0, j = -1):
        operator_location = self._last_outside_parenthesis(["*", "/"], i, j)
        if(operator_location != -1 and operator_location != i):
            token = self.tokens[operator_location]
            return BinaryOperation(
                token.value, 
                self._parse_multiplicative(i, operator_location),
                self._parse_unary(operator_location+1, j),
                # self._parse_pointer_to_member(operator_location+1, j),
                token)

        return self._parse_unary(i, j)
        # return self._parse_pointer_to_member(i, j)
    
    def _parse_additive(self, i = 0, j = -1):
        operator_location = self._last_outside_parenthesis(["+", "-"], i, j)

        if(operator_location != -1 and operator_location != i):
            token = self.tokens[operator_location]
            return BinaryOperation(
                token.value, 
                self._parse_additive(i, operator_location),
                self._parse_multiplicative(operator_location+1, j),
                token)
        
        return self._parse_multiplicative(i, j)
        
    def _parse_shift(self, i = 0, j = -1):
        operator_location = self._last_outside_parenthesis(["<<", ">>"], i, j)
        if(operator_location != -1):
            token = self.tokens[operator_location]
            
            if(operator_location == i):
                raise CompilerSyntaxError(f"Missing operand for {token.value}", token.line, token)
            
            return BinaryOperation(
                token.value, 
                self._parse_shift(i, operator_location),
                self._parse_additive(operator_location+1, j),
                token)
        
        return self._parse_additive(i, j)
    
    def _parse_three_way_compare(self, i = 0, j = -1):
        operator_location = self._last_outside_parenthesis(["<=>"], i, j)
        if(operator_location != -1):
            token = self.tokens[operator_location]
            
            if(operator_location == i):
                raise CompilerSyntaxError(f"Missing operand for {token.value}", token.line, token)
            
            return BinaryOperation(
                token.value, 
                self._parse_three_way_compare(i, operator_location),
                self._parse_shift(operator_location+1, j),
                token)
        
        return self._parse_shift(i, j)
    
    def _parse_relational_compare(self, i = 0, j = -1):
        operator_location = self._last_outside_parenthesis(["<", ">", "<=", ">="], i, j)
        if(operator_location != -1):
            token = self.tokens[operator_location]
            
            if(operator_location == i):
                raise CompilerSyntaxError(f"Missing operand for {token.value}", token.line, token)
            
            return BinaryOperation(
                token.value, 
                self._parse_relational_compare(i, operator_location),
                self._parse_three_way_compare(operator_location+1, j),
                token)
        
        return self._parse_three_way_compare(i, j)
        
    def _parse_equality_compare(self, i = 0, j = -1):
        operator_location = self._last_outside_parenthesis(["==", "!="], i, j)
        if(operator_location != -1):
            token = self.tokens[operator_location]
            
            if(operator_location == i):
                raise CompilerSyntaxError(f"Missing operand for {token.value}", token.line, token)
            
            return BinaryOperation(
                token.value, 
                self._parse_equality_compare(i, operator_location),
                self._parse_relational_compare(operator_location+1, j),
                token)
        
        return self._parse_relational_compare(i, j)
        
    def _parse_bitwise_and(self, i = 0, j = -1):
        operator_location = self._last_outside_parenthesis(["&"], i, j)
        if(operator_location != -1 and operator_location != i):
            token = self.tokens[operator_location]
            return BinaryOperation(
                token.value, 
                self._parse_bitwise_and(i, operator_location),
                self._parse_equality_compare(operator_location+1, j),
                token)
        
        return self._parse_equality_compare(i, j)
        
    def _parse_bitwise_xor(self, i = 0, j = -1):
        operator_location = self._last_outside_parenthesis(["^"], i, j)
        if(operator_location != -1):
            token = self.tokens[operator_location]
            
            if(operator_location == i):
                raise CompilerSyntaxError(f"Missing operand for {token.value}", token.line, token)
            
            return BinaryOperation(
                token.value, 
                self._parse_bitwise_xor(i, operator_location),
                self._parse_bitwise_and(operator_location+1, j),
                token)
        return self._parse_bitwise_and(i, j)
    
    def _parse_bitwise_or(self, i = 0, j = -1):
        operator_location = self._last_outside_parenthesis(["|"], i, j)
        if(operator_location != -1):
            token = self.tokens[operator_location]
            
            if(operator_location == i):
                raise CompilerSyntaxError(f"Missing operand for {token.value}", token.line, token)
            
            return BinaryOperation(
                token.value, 
                self._parse_bitwise_or(i, operator_location),
                self._parse_bitwise_xor(operator_location+1, j),
                token)

        return self._parse_bitwise_xor(i, j)
    def _parse_logical_and(self, i = 0, j = -1):
        operator_location = self._last_outside_parenthesis(["&&"], i, j)
        if(operator_location != -1):
            token = self.tokens[operator_location]
            
            if(operator_location == i):
                raise CompilerSyntaxError(f"Missing operand for {token.value}", token.line, token)
            
            return BinaryOperation(
                token.value, 
                self._parse_logical_and(i, operator_location),
                self._parse_bitwise_or(operator_location+1, j),
                token)

        return self._parse_bitwise_or(i, j)
    
    def _parse_logical_or(self, i = 0, j = -1):
        operator_location = self._last_outside_parenthesis(["||"], i, j)
        if(operator_location != -1):
            token = self.tokens[operator_location]
            
            if(operator_location == i):
                raise CompilerSyntaxError(f"Missing operand for {token.value}", token.line, token)
            
            return BinaryOperation(
                token.value, 
                self._parse_logical_or(i, operator_location),
                self._parse_logical_and(operator_location+1, j),
                token)

        return self._parse_logical_and(i, j)
    
    def _parse_conditional(self, i = 0, j = -1) -> Tuple[SyntaxTree, Tuple[int, int]]:
        
        ternary_operator_location = self._first_outside_parenthesis(["?"], i, j)
        if(ternary_operator_location != -1):
            ternary_tree = SyntaxTree(SyntaxTree.EXPRESSION, "?", self.tokens[ternary_operator_location].value)
            tree = self._parse_logical_or(i, ternary_operator_location)
            ternary_operator_else_location = self._first_outside_parenthesis([":"], ternary_operator_location, j)
            ternary_tree.children.append(tree)
            tree = self._parse_expression(ternary_operator_location + 1, ternary_operator_else_location)

            if(ternary_operator_else_location == -1):
                raise SyntaxError(f"Missing else in ternary operator at line {self.tokens[ternary_operator_location].value}")

            ternary_tree.children.append(tree)
            tree = self._parse_conditional(ternary_operator_else_location + 1, j)

            ternary_tree.children.append(tree)
            return ternary_tree

        return self._parse_logical_or(i, j)

    def _parse_expression(self, i = 0, j = -1):
        return self._parse_assignment(i, j)
    
    def _parse_assignment(self, i = 0, j = -1):
        operator_location = self._first_outside_parenthesis(["=", "+=", "-=", "*=", "/=", "~=", ">>=", "<<=", "^=", "%=", "&=", "|="], i, j)
        if(operator_location != -1):
            token = self.tokens[operator_location]
            
            if(operator_location == j-1):
                raise CompilerSyntaxError(f"Missing operand for {token.value}", token.line, token)
            
            return AssignmentOperation(
                token.value, 
                self._parse_unary(i, operator_location),
                self._parse_assignment(operator_location+1, j),
                token)

        return self._parse_conditional(i, j)

    def _find_matching_parenthesis(self, start_index, end_index):
        stack = 0
        for k in range(start_index, end_index):
            if self.tokens[k].value == "(":
                stack += 1
            elif self.tokens[k].value == ")":
                stack -= 1
                if stack == 0:
                    return k
        return -1

    def _find_split_points(self, start, end, delimiter):
        points = []
        stack = 0
        for k in range(start, end):
            if self.tokens[k].value in ["(", "[", "{"]: stack += 1
            elif self.tokens[k].value in [")", "]", "}"]: stack -= 1
            
            if stack == 0 and self.tokens[k].value == delimiter:
                points.append(k)
        return points

    def _parse_while(self, i, j):
        open_paren = i + 1
        close_paren = self.parenthesis_skip_list[i+1]

        condition = self._parse_expression(open_paren + 1, close_paren)
        body, i = self._parse_statement(close_paren + 1, j)

        tree = SyntaxTree(SyntaxTree.WHILE_STATEMENT, "while", self.tokens[i].value)
        tree.children = [condition, body]
        
        return [ tree ], i

    def _parse_for(self, i, j):
        open_paren = i + 1
        close_paren = self.parenthesis_skip_list[i+1]
        
        semi_locs = self._find_split_points(open_paren + 1, close_paren, ";")
        
        if len(semi_locs) != 2:
            raise SyntaxError(f"Invalid for-loop syntax. Expected 'for(init; cond; update)' at line {self.tokens[i].line}")

        init_tree = []
        if(self._is_token_a_type(self.tokens[open_paren + 1])):
            init_tree = BlockStatement(self._parse_declaration(open_paren + 1, semi_locs[0]), self.tokens[open_paren + 1])
        else:
            init_tree = [self._parse_expression(open_paren + 1, semi_locs[0])]

        cond_tree = self._parse_expression(semi_locs[0] + 1, semi_locs[1])
        update_tree = self._parse_expression(semi_locs[1] + 1, close_paren)


            
        
        body_tree, i = self._parse_statement(close_paren + 1, j)


        loop_tree = WhileStatement(
            cond_tree,
            BlockStatement(body_tree + [update_tree], self.tokens[i]),
        )


        tree = BlockStatement(init_tree + [loop_tree], self.tokens[i])
        # tree = SyntaxTree(SyntaxTree.FOR_STATEMENT, "for", self.tokens[i].value)
        # tree.children = [init_tree, cond_tree, update_tree, body_tree]
        return [tree], i
    
    
    def _parse_block(self, i: int, j: int):
        statements = []
        block_end = self.parenthesis_skip_list[i]
        i += 1
        while(i < block_end):
            statement, i = self._parse_statement(i, block_end)
            if(statement is not None):
                statements += statement

        return [BlockStatement(statements, self.tokens[i])], i + 1


    def _parse_if(self, i, j):
        open_paren = i + 1
        close_paren = self.parenthesis_skip_list[open_paren]

        condition = self._parse_expression(open_paren + 1, close_paren)
        then_body, i = self._parse_statement(close_paren + 1, j)
        
        else_body = [None]
        if i < j and self.tokens[i].value == "else":
            else_body, i = self._parse_statement(i + 1, j)
        
        tree = ConditionalStatement(condition, then_body[0], else_body[0], self.tokens[i])

        return [tree], i


    def _parse_statement(self, i, j) -> tuple[list[SyntaxTree], int]:
        if i >= j:
            return None

        if self.tokens[i].value == "{":
            return self._parse_block(i, j)
        
        if self.tokens[i].value == "while":
            return self._parse_while(i, j)
        
        if self.tokens[i].value == "for":
            return self._parse_for(i, j)
        
        if self.tokens[i].value == "if":
            return self._parse_if(i, j)


        statement_end = self._first_outside_parenthesis([";"], i, j)
        if self._is_token_a_type(self.tokens[i]):
            return self._parse_declaration(i, statement_end), statement_end + 1
        
        if(self.tokens[i].value == "return"):
            return [ReturnStatement(self._parse_expression(i+1, statement_end), self.tokens[i])], statement_end + 1
        return [self._parse_expression(i, statement_end)], statement_end + 1

        # raise CompilerSyntaxError("Unexpected token when parsing statement.", self.tokens[i].line, self.tokens[i])
    

    def _is_token_a_type(self, token:Token):
        return token.type == LexicalAnalyzer.KEYWORD and token.value in [
            "char",
            "char8_t",
            "char16_t",
            "char32_t",
            "double",
            "float",
            "int",
            "long",
            "short",
            "wchar_t",
        ]
    
    
    def _is_token_a_pointer(self, token: Token):
        return token.type == LexicalAnalyzer.OPERATOR and token.value in [
            "*"
        ]
    def _is_token_a_identifier(self, token: Token):
        return token.type == LexicalAnalyzer.IDENTIFIER
    
    def _is_token_a_open_parenthesis(self, token: Token):
        return token.type == LexicalAnalyzer.SEPARATOR and token.value in [
            "("
        ]
    def _is_token_a_closing_parenthesis(self, token: Token):
        return token.type == LexicalAnalyzer.SEPARATOR and token.value in [
            ")"
        ]
    def _is_token_a_comma(self, token: Token):
        return token.type == LexicalAnalyzer.SEPARATOR and token.value in [
            ","
        ]
    def _is_token_a_equal(self, token: Token):
        return token.type == LexicalAnalyzer.OPERATOR and token.value in [
            "="
        ]
    
    
    
    
    
    
    def _parse_declaration(self, i:int, j:int):
        state = 0
        _type = []
        statements = []
        pointer_count = 0
        identifier : Token | None = None
        
        return_type : CType | None = None
        
        
        parameter_list = []
        parameter_types = []
        parameter_pointer_count = 0
        while(i < j):
            curr = self.tokens[i]
            match(state):
                case 0:
                    if(self._is_token_a_type(curr)):
                        _type.append(curr)
                        state = 1
                        pointer_count = 0
                    else:
                        raise CompilerSyntaxError("Missing type in declaration", self.tokens[i-1].line, self.tokens[i-1])
                case 1:
                    if(self._is_token_a_type(curr)):
                        _type.append(curr)
                        state = 1
                    elif(self._is_token_a_pointer(curr)):
                        pointer_count += 1
                        state = 2
                    elif(self._is_token_a_identifier(curr)):
                        identifier = curr
                        state = 3
                    else:
                        raise CompilerSyntaxError("Unexpected token in variable declaration", self.tokens[i-1].line, self.tokens[i-1])
                case 2:
                    if(self._is_token_a_pointer(curr)):
                        pointer_count += 1
                        state = 2
                    elif(self._is_token_a_identifier(curr)):
                        identifier = curr
                        state = 3
                    else:
                        raise CompilerSyntaxError("Unexpected token in variable declaration", self.tokens[i-1].line, self.tokens[i-1])
                case 3:
                    if(self._is_token_a_open_parenthesis(curr)):
                        return_type = CType(
                                    " ".join([token.value for token in _type]),
                                    pointer_count
                                )
                        state = 4
                    elif(self._is_token_a_comma(curr)):
                        statements.append(
                            VariableDeclaration(
                                identifier.value,
                                CType(
                                    " ".join([token.value for token in _type]),
                                    pointer_count
                                ),
                                identifier
                            )
                        )
                        state = 2
                        pointer_count = 0
                    elif(self._is_token_a_equal(curr)):
                        
                        statements.append(
                            VariableDeclaration(
                                identifier.value,
                                CType(
                                    " ".join([token.value for token in _type]),
                                    pointer_count
                                ),
                                identifier
                            )
                        )
                        state = 9
                    else:
                        raise CompilerSyntaxError("Unexpected token in variable declaration", self.tokens[i-1].line, self.tokens[i-1])
                        
                case 4:
                    if(self._is_token_a_type(curr)):
                        state = 5
                        parameter_types = [curr]
                        parameter_pointer_count = 0
                    else:
                        raise CompilerSyntaxError("Missing type in function parameter declaration", self.tokens[i-1].line, self.tokens[i-1])
                
                case 5:
                    if(self._is_token_a_type(curr)):
                        state = 5
                        parameter_types.append(curr)
                    elif(self._is_token_a_pointer(curr)):
                        parameter_pointer_count += 1
                        state = 6
                    elif(self._is_token_a_identifier(curr)):
                        state = 7
                    elif(self._is_token_a_comma(curr)):
                        parameter_list.append(
                            CType(
                                " ".join([token.value for token in parameter_types]),
                                parameter_pointer_count
                            )
                        )
                        state = 4
                    elif(self._is_token_a_closing_parenthesis(curr)):
                        parameter_list.append(
                            CType(
                                " ".join([token.value for token in parameter_types]),
                                parameter_pointer_count
                            )
                        )
                        statements.append(
                            FunctionDeclaration(identifier,return_type, parameter_list, identifier)
                        )
                        state = 8
                    else:
                        raise CompilerSyntaxError("Unexpected token in function parameter declaration", self.tokens[i-1].line, self.tokens[i-1])
                        
                case 6:
                    if(self._is_token_a_pointer(curr)):
                        parameter_pointer_count += 1
                        state = 6
                    elif(self._is_token_a_identifier(curr)):
                        state = 7
                    elif(self._is_token_a_comma(curr)):
                        parameter_list.append(
                            CType(
                                " ".join([token.value for token in parameter_types]),
                                parameter_pointer_count
                            )
                        )
                        state = 4
                    elif(self._is_token_a_closing_parenthesis(curr)):
                        parameter_list.append(
                            CType(
                                " ".join([token.value for token in parameter_types]),
                                parameter_pointer_count
                            )
                        )
                        statements.append(
                            FunctionDeclaration(identifier,return_type, parameter_list, identifier)
                        )
                        state = 8
                    else:
                        raise CompilerSyntaxError("Unexpected token in function parameter declaration", self.tokens[i-1].line, self.tokens[i-1])
                case 7:
                    if(self._is_token_a_comma(curr)):
                        parameter_list.append(
                            CType(
                                " ".join([token.value for token in parameter_types]),
                                parameter_pointer_count
                            )
                        )
                        state = 4
                    elif(self._is_token_a_closing_parenthesis(curr)):
                        parameter_list.append(
                            CType(
                                " ".join([token.value for token in parameter_types]),
                                parameter_pointer_count
                            )
                        )
                        statements.append(
                            FunctionDeclaration(identifier,return_type, parameter_list, identifier)
                        )
                        state = 8
                    else:
                        raise CompilerSyntaxError("Unexpected token in function parameter declaration", self.tokens[i-1].line, self.tokens[i-1])
                case 8:
                    if(self._is_token_a_comma(curr)):
                        state = 2
                        pointer_count = 0
                    else:
                        raise CompilerSyntaxError("Unexpected token in function parameter declaration", self.tokens[i-1].line, self.tokens[i-1])
                    
                
                case 9:
                    i += 1
                    expression_start = i-3
                    state = 10
                    while(i < j):
                        curr = self.tokens[i]
                        if(self._is_token_a_open_parenthesis(curr)):
                            i = self.parenthesis_skip_list[i]
                        elif(self._is_token_a_comma(curr)):
                            state = 2
                            break
                        i += 1

                    statements.append(self._parse_expression(expression_start, i))
            i += 1

        if(state not in [3, 8, 10]):
            raise CompilerSyntaxError("Unexpected end in variable declaration", self.tokens[i-1].line, self.tokens[i-1])
            
        
        return statements
    
    def _parse_function_definition(self, i, j):
        state = 0
        _type = []
        pointer_count = 0
        identifier : Token | None = None
        
        return_type : CType | None = None
        
        
        parameter_list = []
        parameter_types = []
        parameter_pointer_count = 0
        parameter_names : list[Token] = []
        while(i < j and state != 8):
            curr = self.tokens[i]
            match(state):
                case 0:
                    if(self._is_token_a_type(curr)):
                        _type.append(curr)
                        state = 1
                        pointer_count = 0
                    else:
                        raise CompilerSyntaxError("Missing type in declaration", self.tokens[i-1].line, self.tokens[i-1])
                case 1:
                    if(self._is_token_a_type(curr)):
                        _type.append(curr)
                        state = 1
                    elif(self._is_token_a_pointer(curr)):
                        pointer_count += 1
                        state = 2
                    elif(self._is_token_a_identifier(curr)):
                        identifier = curr
                        state = 3
                    else:
                        raise CompilerSyntaxError("Unexpected token in function declaration", self.tokens[i-1].line, self.tokens[i-1])
                case 2:
                    if(self._is_token_a_pointer(curr)):
                        pointer_count += 1
                        state = 2
                    elif(self._is_token_a_identifier(curr)):
                        identifier = curr
                        state = 3
                    else:
                        raise CompilerSyntaxError("Unexpected token in function declaration", self.tokens[i-1].line, self.tokens[i-1])
                case 3:
                    if(self._is_token_a_open_parenthesis(curr)):
                        return_type = CType(
                                    " ".join([token.value for token in _type]),
                                    pointer_count
                                )
                        state = 9
                    else:
                        raise CompilerSyntaxError("Unexpected token in variable declaration", self.tokens[i-1].line, self.tokens[i-1])
                        
                case 4:
                    if(self._is_token_a_type(curr)):
                        state = 5
                        parameter_types = [curr]
                        parameter_pointer_count = 0
                    else:
                        raise CompilerSyntaxError("Missing type in function parameter declaration", self.tokens[i-1].line, self.tokens[i-1])
                
                case 9:
                    if(self._is_token_a_type(curr)):
                        state = 5
                        parameter_types = [curr]
                        parameter_pointer_count = 0
                    elif(self._is_token_a_closing_parenthesis(curr)):
                        state = 8
                    else:
                        raise CompilerSyntaxError("Missing type in function parameter declaration", self.tokens[i-1].line, self.tokens[i-1])
                
                case 5:
                    if(self._is_token_a_type(curr)):
                        state = 5
                        parameter_types.append(curr)
                    elif(self._is_token_a_pointer(curr)):
                        parameter_pointer_count += 1
                        state = 6
                    elif(self._is_token_a_identifier(curr)):
                        parameter_names.append(curr)
                        state = 7
                    else:
                        raise CompilerSyntaxError("Unexpected token in function parameter declaration", self.tokens[i-1].line, self.tokens[i-1])
                        
                case 6:
                    if(self._is_token_a_pointer(curr)):
                        parameter_pointer_count += 1
                        state = 6
                    elif(self._is_token_a_identifier(curr)):
                        parameter_names.append(curr)
                        state = 7
                    else:
                        raise CompilerSyntaxError("Unexpected token in function parameter declaration", self.tokens[i-1].line, self.tokens[i-1])
                case 7:
                    if(self._is_token_a_comma(curr)):
                        parameter_list.append(
                            CType(
                                " ".join([token.value for token in parameter_types]),
                                parameter_pointer_count
                            )
                        )
                        state = 4
                    elif(self._is_token_a_closing_parenthesis(curr)):
                        parameter_list.append(
                            CType(
                                " ".join([token.value for token in parameter_types]),
                                parameter_pointer_count
                            )
                        )
                        state = 8
                    else:
                        raise CompilerSyntaxError("Unexpected token in function parameter declaration", self.tokens[i-1].line, self.tokens[i-1])
                
            i += 1
        
        if(self.tokens[i].value != "{"):
            raise CompilerSyntaxError("Missing function body", self.tokens[i].line, self.tokens[i])
        
        if(state not in [8]):
            raise CompilerSyntaxError("Unexpected end in function declaration", self.tokens[i-1].line, self.tokens[i-1])

            
        body, i = self._parse_block(i, j)
        return FunctionDefinition(
                            identifier.value,
                            return_type,
                            list(zip([ n.value for n in parameter_names], parameter_list)),
                            body[0],
                            identifier
                        )

    def _parse_external_statement(self, i, j):
        if self.tokens[j-1].value == ";":
            return self._parse_declaration(i, j-1)
        if self.tokens[j-1].value == "}":
            return self._parse_function_definition(i, j)

        raise CompilerSyntaxError("Unexpected token when parsing statement.", self.tokens[i].line, self.tokens[i])

    def _parse_external_statements(self, i, j):
        statements = []
        last_statement_start = i
        while(i < j):
            if(self.parenthesis_skip_list[i] != -1):
                i = self.parenthesis_skip_list[i]
            
            if(self.tokens[i].value == ";" or self.tokens[i].value == "}"):
                statements.append(self._parse_external_statement(last_statement_start, i+1))
                last_statement_start = i + 1
            
            i += 1

        return ExternalBlockStatement(statements, self.tokens[i-1])

    def _analyze_parenthesis(self, tokens : List[Token]) -> List[int]:
        sta = []
        out = [ -1 for _ in tokens ]

        for i, curr in enumerate(tokens):
            if(curr.value == "(" and curr.type == LexicalAnalyzer.SEPARATOR):
                sta.append((0, i))
            elif(curr.value == "[" and curr.type == LexicalAnalyzer.SEPARATOR):
                sta.append((1, i))
            elif(curr.value == "{" and curr.type == LexicalAnalyzer.SEPARATOR):
                sta.append((2, i))
            elif(curr.value == ")" and curr.type == LexicalAnalyzer.SEPARATOR):
                if(len(sta) == 0 or sta[-1][0] != 0):
                    raise CompilerSyntaxError(
                        message="Unmatched closing parenthesis",
                        line=curr.line,
                        token_content=curr)
                _, index = sta.pop()
                out[i] = index
                out[index] = i
            elif(curr.value == "]" and curr.type == LexicalAnalyzer.SEPARATOR):
                if(len(sta) == 0 or sta[-1][0] != 1):
                    raise CompilerSyntaxError(
                        message="Unmatched closing square bracket",
                        line=curr.line,
                        token_content=curr)
                _, index = sta.pop()
                out[i] = index
                out[index] = i
            elif(curr.value == "}" and curr.type == LexicalAnalyzer.SEPARATOR):
                if(len(sta) == 0 or sta[-1][0] != 2):
                    raise CompilerSyntaxError(
                        message="Unmatched closing curly brace",
                        line=curr.line,
                        token_content=curr)
                _, index = sta.pop()
                out[i] = index
                out[index] = i
        
        if(len(sta) != 0):
            opening_type, opening_index = sta[-1]
            opening_token = tokens[opening_index]
            if opening_type == 0:
                message = "Unmatched opening parenthesis"
            elif opening_type == 1:
                message = "Unmatched opening square bracket"
            else:
                message = "Unmatched opening curly brace"
            raise CompilerSyntaxError(
                message=message,
                line=opening_token.line,
                token_content=opening_token)


        return out


    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.parenthesis_skip_list = self._analyze_parenthesis(self.tokens)

    def analyze(self):
        return self._parse_external_statements(0, len(self.tokens))
