from typing import *
from lexer import LexicalAnalyzer
from errors import CompilationError

class SyntaxTree:
    EXPRESSION = 0
    IDENTIFIER = 1
    NUMERIC_LITERAL = 2
    WHILE_STATEMENT = 3
    FOR_STATEMENT = 4
    BLOCK_STATEMENT = 5

    NAME = ["EXPRESSION", "IDENTIFIER", "NUMERIC_LITERAL","WHILE", "FOR", "BLOCK"]

    _id = 0



    def __init__(self, typ, expression_type, line=0):
        self.children = []
        self.type = typ
        self.expression_type = expression_type
        self.value = 0
        self.line = line

        self.id = SyntaxTree._id
        SyntaxTree._id += 1

        self.data_type = None
    
    def __str__(self):
        return str(self.id) + " " + SyntaxTree.NAME[self.type] + " " + str(self.expression_type) + " " + ",".join([str(i.id) if i is not None else "None" for i in self.children]) + "\n" + "\n".join([str(i) for i in self.children])



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

    def _is_keyword(self, tokens : List[Tuple[str, int, int]], i = 0, keyword : str | None = None):
        if(tokens[i][1] != LexicalAnalyzer.KEYWORD):
            return False
        return tokens[i][0] == keyword if keyword != None else True

    def _is_operator(self, tokens : List[Tuple[str, int, int]], i = 0, operator : str | None = None):
        if(tokens[i][1] != LexicalAnalyzer.OPERATOR):
            return False
        return tokens[i][0] == operator if operator != None else True

    def _analyze_if_self(self, tokens : List[Tuple[str, int, int]], i = 0):
        if(self._is_keyword(tokens, i, "if")):
            pass
    
    def _first_outside_parenthesis(self, tokens : List[Tuple[str, int, int]], matches, i = 0, j = -1, ):
        j = len(tokens) if j == -1 else j

        sta = []

        while(i < j):
            curr = tokens[i]
            if(curr[0] in matches and len(sta) == 0):
                return i
            if(curr[0] == "(" and curr[1] == LexicalAnalyzer.SEPARATOR):
                sta.append(0)
            elif(curr[0] == "[" and curr[1] == LexicalAnalyzer.SEPARATOR):
                sta.append(1)
            elif(curr[0] == "{" and curr[1] == LexicalAnalyzer.SEPARATOR):
                sta.append(2)
            elif(curr[0] == ")" and curr[1] == LexicalAnalyzer.SEPARATOR):
                if(len(sta) == 0 or sta[-1] != 0):
                    return -1
                sta.pop()
            elif(curr[0] == "]" and curr[1] == LexicalAnalyzer.SEPARATOR):
                if(len(sta) == 0 or sta[-1] != 1):
                    return -1
                sta.pop()
            elif(curr[0] == "}" and curr[1] == LexicalAnalyzer.SEPARATOR):
                if(len(sta) == 0 or sta[-1] != 2):
                    return -1
                sta.pop()
            i += 1
        return -1
    
    def _last_outside_parenthesis(self, tokens : List[Tuple[str, int]], matches, i = 0, j = -1):
        j = len(tokens) - 1 if j == -1 else j - 1

        sta = []

        while(i <= j):
            curr = tokens[j]
            if(curr[0] in matches and len(sta) == 0):
                return j
            if(curr[0] == ")" and curr[1] == LexicalAnalyzer.SEPARATOR):
                sta.append(0)
            elif(curr[0] == "]" and curr[1] == LexicalAnalyzer.SEPARATOR):
                sta.append(1)
            elif(curr[0] == "}" and curr[1] == LexicalAnalyzer.SEPARATOR):
                sta.append(2)
            elif(curr[0] == "(" and curr[1] == LexicalAnalyzer.SEPARATOR):
                if(len(sta) == 0 or sta[-1] != 0):
                    return -1
                sta.pop()
            elif(curr[0] == "[" and curr[1] == LexicalAnalyzer.SEPARATOR):
                if(len(sta) == 0 or sta[-1] != 1):
                    return -1
                sta.pop()
            elif(curr[0] == "{" and curr[1] == LexicalAnalyzer.SEPARATOR):
                if(len(sta) == 0 or sta[-1] != 2):
                    return -1
                sta.pop()
            j -= 1
        return -1

    def _parse_primary(self, tokens : List[Tuple[str, int, int]], i = 0, j = -1):
        if(i == j) :
            prev_line = tokens[i-1][2] if i > 0 else 0
            raise CompilationError("Expected expression", prev_line)
        

        if(j - i > 1):
            if(tokens[i][0] == "(" and tokens[j-1][0] == ")"):
                return self._parse_expression(tokens, i + 1, j - 1)
        else:
            if(tokens[i][1] == LexicalAnalyzer.HEX_LITERAL):
                a = SyntaxTree(SyntaxTree.NUMERIC_LITERAL, tokens[i][0], tokens[i][2])
                a.value = str(int(tokens[i][0][2:], base=16))
                return a
            if(tokens[i][1] == LexicalAnalyzer.NUM_LITERAL):
                a = SyntaxTree(SyntaxTree.NUMERIC_LITERAL, tokens[i][0], tokens[i][2])
                a.value = str(int(tokens[i][0], base=16))
                return a

            return SyntaxTree(SyntaxTree.IDENTIFIER, tokens[i][0], tokens[i][2])
        
    def _parse_postfix(self, tokens : List[Tuple[str, int, int]], i = 0, j = -1):
        if(j - i > 1):
            operator = tokens[j-1][0]
            if(operator in ["++", "--"]):
                new_tree = SyntaxTree(SyntaxTree.EXPRESSION, operator, tokens[j-1][2])
                new_tree.children = [
                    self._parse_postfix(tokens, i, j-1),
                ]
                return new_tree
            if(operator == "]"):
                operator_location = self._last_outside_parenthesis(tokens, ["["], i, j-1)
                if(operator_location != i):
                    new_tree = SyntaxTree(SyntaxTree.EXPRESSION, "[]", tokens[j-1][2])
                    new_tree.children = [
                        self._parse_postfix(tokens, i, operator_location),
                        self._parse_expression(tokens, operator_location + 1, j - 1)
                    ]
                    return new_tree

            if(operator == ")"):
                operator_location = self._last_outside_parenthesis(tokens, ["("], i, j-1)
                if(operator_location != i):
                    new_tree = SyntaxTree(SyntaxTree.EXPRESSION, "()", tokens[j-1][2])
                    new_tree.children = [
                        self._parse_postfix(tokens, i, operator_location),
                        self._parse_expression(tokens, operator_location + 1, j - 1)
                    ]
                    return new_tree
            

        if(j - i > 2):
            operator = tokens[j-2][0]
            if(operator in ["->", "*"] and j-2 != i):
                new_tree = SyntaxTree(SyntaxTree.EXPRESSION, operator, tokens[j-2][2])
                new_tree.children = [
                    self._parse_postfix(tokens, i, j-2),
                    SyntaxTree(SyntaxTree.IDENTIFIER, tokens[j-1])
                ]
                return new_tree

        return self._parse_primary(tokens, i, j)

    def _parse_unary(self, tokens : List[Tuple[str, int, int]], i = 0, j = -1):
        if(tokens[i][0] in ["++", "--", "-", "+", "!", "~", "*", "&", "sizeof"]):
            new_tree = SyntaxTree(SyntaxTree.EXPRESSION, tokens[i][0]+"_pre", tokens[i][2])
            new_tree.children = [
                self._parse_unary(tokens, i + 1, j),
            ]
            return new_tree
        
        return self._parse_postfix(tokens, i, j)
    
    def _parse_pointer_to_member(self, tokens : List[Tuple[str, int]], i = 0, j = -1):
        operator_location = self._last_outside_parenthesis(tokens, ["->*", ".*"], i, j)
        if(operator_location != -1 and operator_location != i):
            new_tree = SyntaxTree(SyntaxTree.EXPRESSION, tokens[operator_location][0])
            new_tree.children = [
                self._parse_pointer_to_member(tokens, i, operator_location),
                self._parse_unary(tokens, operator_location+1, j)
            ]
            return new_tree

        return self._parse_unary(tokens, i, j)
    def _parse_multiplicative(self, tokens : List[Tuple[str, int, int]], i = 0, j = -1):
        operator_location = self._last_outside_parenthesis(tokens, ["*", "/"], i, j)
        if(operator_location != -1 and operator_location != i):
            new_tree = SyntaxTree(SyntaxTree.EXPRESSION, tokens[operator_location][0], tokens[operator_location][2])
            new_tree.children = [
                self._parse_multiplicative(tokens, i, operator_location),
                self._parse_pointer_to_member(tokens, operator_location+1, j)
            ]
            return new_tree

        return self._parse_pointer_to_member(tokens, i, j)
    
    def _parse_additive(self, tokens : List[Tuple[str, int, int]], i = 0, j = -1):
        operator_location = self._last_outside_parenthesis(tokens, ["+", "-"], i, j)

        if(operator_location != -1 and operator_location != i):
            new_tree = SyntaxTree(SyntaxTree.EXPRESSION, tokens[operator_location][0], tokens[operator_location][2])
            new_tree.children = [
                self._parse_additive(tokens, i, operator_location),
                self._parse_multiplicative(tokens, operator_location+1, j)
            ]
            return new_tree
        
        return self._parse_multiplicative(tokens, i, j)
        
    def _parse_shift(self, tokens : List[Tuple[str, int]], i = 0, j = -1):
        operator_location = self._last_outside_parenthesis(tokens, ["<<", ">>"], i, j)
        if(operator_location != -1 and operator_location != i):
            new_tree = SyntaxTree(SyntaxTree.EXPRESSION, tokens[operator_location][0])
            new_tree.children = [
                self._parse_shift(tokens, i, operator_location),
                self._parse_additive(tokens, operator_location+1, j)
            ]
            return new_tree
        
        return self._parse_additive(tokens, i, j)
    
    def _parse_three_way_compare(self, tokens : List[Tuple[str, int]], i = 0, j = -1):
        operator_location = self._last_outside_parenthesis(tokens, ["<=>"], i, j)
        if(operator_location != -1 and operator_location != i):
            new_tree = SyntaxTree(SyntaxTree.EXPRESSION, tokens[operator_location][0])
            new_tree.children = [
                self._parse_three_way_compare(tokens, i, operator_location),
                self._parse_shift(tokens, operator_location+1, j)
            ]
            return new_tree
        
        return self._parse_shift(tokens, i, j)
    
    def _parse_relational_compare(self, tokens : List[Tuple[str, int]], i = 0, j = -1):
        operator_location = self._last_outside_parenthesis(tokens, ["<", ">", "<=", ">="], i, j)
        if(operator_location != -1 and operator_location != i):

            new_tree = SyntaxTree(SyntaxTree.EXPRESSION, tokens[operator_location][0])
            new_tree.children = [
                self._parse_relational_compare(tokens, i, operator_location),
                self._parse_three_way_compare(tokens, operator_location+1, j)
            ]
            return new_tree
        
        return self._parse_three_way_compare(tokens, i, j)
        
    def _parse_equality_compare(self, tokens : List[Tuple[str, int]], i = 0, j = -1):
        operator_location = self._last_outside_parenthesis(tokens, ["==", "!="], i, j)
        if(operator_location != -1):
            if(operator_location == i): 
                raise SyntaxError()
            
            new_tree = SyntaxTree(SyntaxTree.EXPRESSION, tokens[operator_location][0])
            new_tree.children = [
                self._parse_equality_compare(tokens, i, operator_location),
                self._parse_relational_compare(tokens, operator_location+1, j)
            ]
            return new_tree
        
        return self._parse_relational_compare(tokens, i, j)
        
    def _parse_bitwise_and(self, tokens : List[Tuple[str, int]], i = 0, j = -1):
        operator_location = self._last_outside_parenthesis(tokens, ["&"], i, j)
        if(operator_location != -1 and operator_location != i):
            new_tree = SyntaxTree(SyntaxTree.EXPRESSION, tokens[operator_location][0])
            new_tree.children = [
                self._parse_bitwise_and(tokens, i, operator_location),
                self._parse_equality_compare(tokens, operator_location+1, j)
            ]
            return new_tree
        
        return self._parse_equality_compare(tokens, i, j)
        
    def _parse_bitwise_xor(self, tokens : List[Tuple[str, int]], i = 0, j = -1):
        operator_location = self._last_outside_parenthesis(tokens, ["^"], i, j)
        if(operator_location != -1):
            if(operator_location == i): 
                raise SyntaxError()
            
            new_tree = SyntaxTree(SyntaxTree.EXPRESSION, tokens[operator_location][0])
            new_tree.children = [
                self._parse_bitwise_xor(tokens, i, operator_location),
                self._parse_bitwise_and(tokens, operator_location+1, j)
            ]
            return new_tree

        return self._parse_bitwise_and(tokens, i, j)
    def _parse_bitwise_or(self, tokens : List[Tuple[str, int]], i = 0, j = -1):
        operator_location = self._last_outside_parenthesis(tokens, ["|"], i, j)
        if(operator_location != -1):
            if(operator_location == i): 
                raise SyntaxError()
            
            new_tree = SyntaxTree(SyntaxTree.EXPRESSION, tokens[operator_location][0])
            new_tree.children = [
                self._parse_bitwise_or(tokens, i, operator_location),
                self._parse_bitwise_xor(tokens, operator_location+1, j)
            ]
            return new_tree

        return self._parse_bitwise_xor(tokens, i, j)
    def _parse_logical_and(self, tokens : List[Tuple[str, int]], i = 0, j = -1):
        operator_location = self._last_outside_parenthesis(tokens, ["&&"], i, j)
        if(operator_location != -1):
            if(operator_location == i): 
                raise SyntaxError()
            new_tree = SyntaxTree(SyntaxTree.EXPRESSION, tokens[operator_location][0])
            new_tree.children = [
                self._parse_logical_and(tokens, i, operator_location),
                self._parse_bitwise_or(tokens, operator_location+1, j)
            ]
            return new_tree

        return self._parse_bitwise_or(tokens, i, j)
    
    def _parse_logical_or(self, tokens : List[Tuple[str, int, int]], i = 0, j = -1):
        operator_location = self._last_outside_parenthesis(tokens, ["||"], i, j)
        if(operator_location != -1):
            if(operator_location == i): 
                raise SyntaxError(f"Invalid logical or operator position at line {tokens[i][2]}")
            new_tree = SyntaxTree(SyntaxTree.EXPRESSION, tokens[operator_location][0], tokens[operator_location][2])
            new_tree.children = [
                self._parse_logical_or(tokens, i, operator_location),
                self._parse_logical_and(tokens, operator_location+1, j)
            ]
            return new_tree

        return self._parse_logical_and(tokens, i, j)
    
    def _parse_conditional(self, tokens : List[Tuple[str, int, int]], i = 0, j = -1) -> Tuple[SyntaxTree, Tuple[int, int]]:
        
        ternary_operator_location = self._first_outside_parenthesis(tokens, ["?"], i, j)
        if(ternary_operator_location != -1):
            ternary_tree = SyntaxTree(SyntaxTree.EXPRESSION, "?", tokens[ternary_operator_location][2])
            tree = self._parse_logical_or(tokens, i, ternary_operator_location)
            ternary_operator_else_location = self._first_outside_parenthesis(tokens, [":"], ternary_operator_location, j)
            ternary_tree.children.append(tree)
            tree = self._parse_expression(tokens, ternary_operator_location + 1, ternary_operator_else_location)

            if(ternary_operator_else_location == -1):
                raise SyntaxError(f"Missing else in ternary operator at line {tokens[ternary_operator_location][2]}")

            ternary_tree.children.append(tree)
            tree = self._parse_conditional(tokens, ternary_operator_else_location + 1, j)

            ternary_tree.children.append(tree)
            return ternary_tree

        return self._parse_logical_or(tokens, i, j)

    def _parse_expression(self, tokens : List[Tuple[str, int]], i = 0, j = -1):
        return self._parse_assignment(tokens, i, j)
    
    def _parse_assignment(self, tokens : List[Tuple[str, int, int]], i = 0, j = -1):
        operator_location = self._first_outside_parenthesis(tokens, ["=", "+=", "-=", "*=", "/=", "~=", ">>=", "<<=", "^=", "%=", "&=", "|="], i, j)
        if(operator_location != -1 and operator_location != j-1):
            new_tree = SyntaxTree(SyntaxTree.EXPRESSION, tokens[operator_location][0], tokens[operator_location][2])
            new_tree.children = [
                self._parse_unary(tokens, i, operator_location),
                self._parse_assignment(tokens, operator_location+1, j)
            ]
            return new_tree

        return self._parse_conditional(tokens, i, j)


    def _find_matching_parenthesis(self, tokens, start_index, end_index):
        stack = 0
        for k in range(start_index, end_index):
            if tokens[k][0] == "(":
                stack += 1
            elif tokens[k][0] == ")":
                stack -= 1
                if stack == 0:
                    return k
        return -1

    def _find_split_points(self, tokens, start, end, delimiter):
        points = []
        stack = 0
        for k in range(start, end):
            if tokens[k][0] in ["(", "[", "{"]: stack += 1
            elif tokens[k][0] in [")", "]", "}"]: stack -= 1
            
            if stack == 0 and tokens[k][0] == delimiter:
                points.append(k)
        return points

    def _parse_while(self, tokens, i, j):
        open_paren = i + 1
        close_paren = self._find_matching_parenthesis(tokens, open_paren, j)
        
        if close_paren == -1:
            raise SyntaxError(f"Missing closing parenthesis in while loop at line {tokens[i][2]}")

        condition = self._parse_expression(tokens, open_paren + 1, close_paren)
        body = self._parse_statement(tokens, close_paren + 1, j)

        tree = SyntaxTree(SyntaxTree.WHILE_STATEMENT, "while", tokens[i][2])
        tree.children = [condition, body]
        return tree

    def _parse_for(self, tokens, i, j):
        open_paren = i + 1
        close_paren = self._find_matching_parenthesis(tokens, open_paren, j)
        
        if close_paren == -1:
            raise SyntaxError(f"Missing closing parenthesis in for loop at line {tokens[i][2]}")
        semi_locs = self._find_split_points(tokens, open_paren + 1, close_paren, ";")
        
        if len(semi_locs) != 2:
            raise SyntaxError(f"Invalid for-loop syntax. Expected 'for(init; cond; update)' at line {tokens[i][2]}")

        init_tree = self._parse_expression(tokens, open_paren + 1, semi_locs[0])
        cond_tree = self._parse_expression(tokens, semi_locs[0] + 1, semi_locs[1])
        update_tree = self._parse_expression(tokens, semi_locs[1] + 1, close_paren)
        
        body_tree = self._parse_statement(tokens, close_paren + 1, j)

        tree = SyntaxTree(SyntaxTree.FOR_STATEMENT, "for", tokens[i][2])
        tree.children = [init_tree, cond_tree, update_tree, body_tree]
        return tree

    def _parse_statement(self, tokens, i, j):
        if i >= j:
            return None

        if tokens[i][0] == "{":
            return self._parse_statement(tokens, i + 1, j - 1)

        if tokens[i][0] == "while":
            return self._parse_while(tokens, i, j)
        
        if tokens[i][0] == "for":
            return self._parse_for(tokens, i, j)
        
        if j > i and tokens[j-1][0] == ";":
            return self._parse_expression(tokens, i, j-1)

        return self._parse_expression(tokens, i, j)
    

    def analyze(self, tokens: list[tuple[str, int, int]]):
        return self._parse_statement(tokens, 0, len(tokens))
