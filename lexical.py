from typing import *
import itertools

KEYWORDS = [
    "alignas",
    "alignof",
    "and",
    "and_eq",
    "asm",
    "atomic_cancel",
    "atomic_commit",
    "atomic_noexcept",
    "auto",
    "bitand",
    "bitor",
    "bool",
    "break",
    "case",
    "catch",
    "char",
    "char8_t",
    "char16_t",
    "char32_t",
    "class",
    "compl",
    "concept",
    "const",
    "consteval",
    "constexpr",
    "constinit",
    "const_cast",
    "continue",
    "contract_assert",
    "co_await",
    "co_return",
    "co_yield",
    "decltype",
    "default",
    "delete",
    "do",
    "double",
    "dynamic_cast",
    "else",
    "enum",
    "explicit",
    "export",
    "extern",
    "false",
    "float",
    "for",
    "friend",
    "goto",
    "if",
    "inline",
    "int",
    "long",
    "mutable",
    "namespace",
    "new",
    "noexcept",
    "not",
    "not_eq",
    "nullptr",
    "operator",
    "or",
    "or_eq",
    "private",
    "protected",
    "public",
    "reflexpr",
    "register",
    "reinterpret_cast",
    "requires",
    "return",
    "short",
    "signed",
    "sizeof",
    "static",
    "static_assert",
    "static_cast",
    "struct",
    "switch",
    "synchronized",
    "template",
    "this",
    "thread_local",
    "throw",
    "true",
    "try",
    "typedef",
    "typeid",
    "typename",
    "union",
    "unsigned",
    "using",
    "virtual",
    "void",
    "volatile",
    "wchar_t",
    "while",
    "xor",
    "xor_eq"
]
OPERATORS = [
    "+",
    "-",
    "*",
    "/",
    "%",

    "++",
    "--",

    "=",
    "+=",
    "-=",
    "*=",
    "/=",
    "%=",
    "&=",
    "|=",
    "^=",
    "+=",
    ">>=",
    "<<=",

    ":=",
    "+=",
    "==",
    "!=",
    "<=",
    ">=",
    "<",
    ">",
    "<=>",
    "&",
    "|",
    "^",
    "~",
    "<<",
    ">>",
    "?",
    "!",
    "&&",
    "||",
    "->",
    "::",
    ".*",
    "->*"
]

OPERATOR_PRECEDENCE = [
    [ ":: "],
    [ ".", "->" ],
    [ "++", "--", "+", "-", "!", "~", "*", "&", "sizeof" ]
]

SEPERATORS = [
    "{", "}", "[", "]", "(", ")", ".", ",", ":", ";", "#"
]


class Trie:
    def __init__(self):
        self.children = {}
        self.value = None
    
    def search_longest(self, s, i = 0):
        curr = self
        j = i
        out = ( None, i )
        while(curr != None and j < len(s)):
            out = ( curr.value, j )
            curr_letter = s[j]

            if(curr_letter not in curr.children):
                return out
            
            curr = curr.children[curr_letter]
            j += 1

        return ( curr.value, j )
        
    def insert(self, s, value, i=0):
        if(len(s) == i):
            self.value = value
            return
        curr_letter = s[i]
        if(curr_letter not in self.children):
            self.children[curr_letter] = Trie()
        self.children[curr_letter].insert(s, value, i+1)

class LexicalAnalyzer:
    KEYWORD = 1
    IDENTIFIER = 2
    OPERATOR = 3
    SEPARATOR = 4
    STRING = 5
    HEX_LITERAL = 6
    BIN_LITERAL = 7
    NUM_LITERAL = 8
    OTHER = -1

    def __init__(self):
        self.keywork_operator_trie = Trie()
        for keyword in KEYWORDS:
            self.keywork_operator_trie.insert(keyword, LexicalAnalyzer.KEYWORD)
        
        for operator in OPERATORS:
            self.keywork_operator_trie.insert(operator, LexicalAnalyzer.OPERATOR)

        for seperator in SEPERATORS:
            self.keywork_operator_trie.insert(seperator, LexicalAnalyzer.SEPARATOR)

    def _starts_with(self, pre, s, i = 0):
        j = 0
        while(i < len(s) and j < len(pre)):
            if(pre[j] != s[i]):
                return False
            j += 1
            i += 1
        return True

    def _parse_integer_literal(self, s, i = 0):
        c = s[i]
        if(not str.isdigit(c)):
            return ( False, i )
        
        while(i < len(s)):
            i += 1
            c = s[i]
            if(not str.isdigit(c)):
                return ( True, i )
        
        return ( True, i ) 
    
    def _parse_hexadecimal_literal(self, s, i = 0):
        c = s[i]
        if(not str.isdigit(c) and c not in "abcdefABCDEF"):
            return ( False, i )
        
        while(i < len(s)):
            i += 1
            c = s[i]
            if(not str.isdigit(c) and c not in "abcdefABCDEF"):
                return ( True, i )
        
        return ( True, i) 
    def _parse_binary_literal(self, s, i = 0):
        c = s[i]
        if(c not in "01"):
            return ( False, i )
        
        while(i < len(s)):
            i += 1
            c = s[i]
            if(c not in "01"):
                return ( True, i )
        
        return ( True, i) 

    def _parse_numeric_literal(self, s, i = 0):
        if(self._starts_with("0x", s, i)):
            return self._parse_hexadecimal_literal(s, i+2) + (LexicalAnalyzer.HEX_LITERAL,)
        if(self._starts_with("0b", s, i)):
            return self._parse_binary_literal(s, i+2) + (LexicalAnalyzer.BIN_LITERAL,)
        return self._parse_floating_point(s, i) + (LexicalAnalyzer.NUM_LITERAL,)

    def _parse_floating_point(self, s, i = 0):
        state = 11
        n = len(s)
        while(i < n):
            curr = s[i]

            match state:
                case 11:
                    if(curr == "+" or curr == "-"):
                        state = 12
                    elif(str.isdigit(curr)):
                        state = 13
                    else:
                        state = 21
                case 12:
                    if(str.isdigit(curr)):
                        state = 13
                    else:
                        state = 21
                case 13:
                    if(str.isdigit(curr)):
                        state = 13
                    elif(curr == "."):
                        state = 14
                    elif(curr == "e" or curr == "E"):
                        state = 16
                    else:
                        state = 20
                case 14:
                    if(str.isdigit(curr)):
                        state = 15
                    else:
                        state = 21
                case 15:
                    if(str.isdigit(curr)):
                        state = 15
                    elif(curr == "e" or curr == "E"):
                        state = 16
                    else:
                        state = 20
                case 16:
                    if(str.isdigit(curr)):
                        state = 18
                    elif(curr == "+" or curr == "-"):
                        state = 17
                    else:
                        state = 21
                case 17:
                    if(str.isdigit(curr)):
                        state = 18
                    else:
                        state = 21
                case 18:
                    if(str.isdigit(curr)):
                        state = 18
                    else:
                        state = 20
            
            if(state == 20 or state == 21):
                break
            
            i += 1

        if(state == 20 or state == 15 or state == 13 or state == 18):
            return ( True, i )

        return ( False, s )


    def _parse_identifier(self, s, i = 0):
        if(len(s) <= i or not (str.isalpha(s[i]) or s[i] == "_" )):
            return ( False, i )
        i += 1
        while(i < len(s) and (str.isalnum(s[i]) or s[i] == "_")):
            i += 1
        return ( True, i )
    
    def _parse_string(self, s, i = 0):
        STRING_DELIMETERS = [ "\"", "'" ]
        if(len(s) <= i or s[i] not in STRING_DELIMETERS):
            return ( False, i, True )
        delim = s[i]
        i += 1
        while(i < len(s)):
            if(s[i] == "\\"):
                i += 1
            elif(s[i] == delim):
                return ( True, i+1, True )
            i += 1
        return ( False, i, False )
        
           
    def _parse_token(self, s, i = 0):
        typ, j = self.keywork_operator_trie.search_longest(s, i)
        if(i != j and typ != None):
            return (typ , j)
                
        is_valid_identifier, j = self._parse_identifier(s, i)
        if(is_valid_identifier):
            return (LexicalAnalyzer.IDENTIFIER, j)
        
        is_valid_string, j, is_valid_token = self._parse_string(s, i)
        if(not is_valid_token):
            raise SyntaxError()
        if(is_valid_string):
            return (LexicalAnalyzer.STRING, j)

        is_valid_numeric_literal, j, typ = self._parse_numeric_literal(s, i)
        if(is_valid_numeric_literal):
            return ( typ, j )
        
        return (None, i+1)

    def analyze(self, s) -> list[tuple[str, int]]:
        i = 0
        n = len(s)

        tokens = []

        while(i < n):
            typ, j = self._parse_token(s, i)
            if(typ != None):
                tokens.append((s[i:j], typ))
            i = j

        typestr = [
            "",
            "KEYWORD",
            "IDENTIFIER",
            "OPERATOR",
            "SEPARATOR",
            "STRING",
            "HEX_LITERAL",
            "BIN_LITERAL",
            "NUM_LITERAL",
            "OTHER"
        ]

        # print(" ".join([tk  for tk, _ in tokens]))
        for tk, typ in tokens:
            print(tk, typestr[typ])
        
        return tokens


class SyntaxTree:
    EXPRESSION = 0
    IDENTIFIER = 1
    NUMERIC_LITERAL = 2

    NAME = ["EXPRESSION", "IDENTIFIER", "NUMERIC_LITERAL"]

    _id = 0



    def __init__(self, typ, expression_type):
        self.children = []
        self.type = typ
        self.expression_type = expression_type
        self.value = 0

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



    # FUNCTION_CALL = 7
    # TYPE_CAST = 8

    OTHER = -1

    def _is_keyword(self, tokens : List[Tuple[str, int]], i = 0, keyword : str | None = None):
        if(tokens[i][1] != LexicalAnalyzer.KEYWORD):
            return False
        return tokens[i][0] == keyword if keyword != None else True

    def _is_operator(self, tokens : List[Tuple[str, int]], i = 0, operator : str | None = None):
        if(tokens[i][1] != LexicalAnalyzer.OPERATOR):
            return False
        return tokens[i][0] == operator if operator != None else True

    def _analyze_if_self(self, tokens : List[Tuple[str, int]], i = 0):
        if(self._is_keyword(tokens, i, "if")):
            pass
    
    def _first_outside_parenthesis(self, tokens : List[Tuple[str, int]], matches, i = 0, j = -1, ):
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

    def _parse_primary(self, tokens : List[Tuple[str, int]], i = 0, j = -1):
        if(i == j) :
            raise SyntaxError()
        
        if(j - i > 1):
            if(tokens[i][0] == "(" and tokens[j-1][0] == ")"):
                return self._parse_expression(tokens, i + 1, j - 1)
            # else:
            #     raise SyntaxError()
        else:
            if(tokens[i][1] == LexicalAnalyzer.HEX_LITERAL):
                a = SyntaxTree(SyntaxTree.NUMERIC_LITERAL, tokens[i][0])
                a.value = str(int(tokens[i][0][2:], base=16))
                return a
            if(tokens[i][1] == LexicalAnalyzer.NUM_LITERAL):
                a = SyntaxTree(SyntaxTree.NUMERIC_LITERAL, tokens[i][0])
                a.value = str(int(tokens[i][0], base=16))
                return a

            return SyntaxTree(SyntaxTree.IDENTIFIER, tokens[i][0])
        
    def _parse_postfix(self, tokens : List[Tuple[str, int]], i = 0, j = -1):
        if(j - i > 1):
            operator = tokens[j-1][0]
            if(operator in ["++", "--"]):
                new_tree = SyntaxTree(SyntaxTree.EXPRESSION, operator)
                new_tree.children = [
                    self._parse_postfix(tokens, i, j-1),
                ]
                return new_tree
            if(operator == "]"):
                operator_location = self._last_outside_parenthesis(tokens, ["["], i, j-1)
                if(operator_location != i):
                    new_tree = SyntaxTree(SyntaxTree.EXPRESSION, "[]")
                    new_tree.children = [
                        self._parse_postfix(tokens, i, operator_location),
                        self._parse_expression(tokens, operator_location + 1, j - 1)
                    ]
                    return new_tree

            if(operator == ")"):
                operator_location = self._last_outside_parenthesis(tokens, ["("], i, j-1)
                if(operator_location != i):
                    new_tree = SyntaxTree(SyntaxTree.EXPRESSION, "()")
                    new_tree.children = [
                        self._parse_postfix(tokens, i, operator_location),
                        self._parse_expression(tokens, operator_location + 1, j - 1)
                    ]
                    return new_tree
            

        if(j - i > 2):
            operator = tokens[j-2][0]
            if(operator in ["->", "*"] and j-2 != i):
                new_tree = SyntaxTree(SyntaxTree.EXPRESSION, operator)
                new_tree.children = [
                    self._parse_postfix(tokens, i, j-2),
                    SyntaxTree(SyntaxTree.IDENTIFIER, tokens[j-1])
                ]
                return new_tree

        return self._parse_primary(tokens, i, j)

    def _parse_unary(self, tokens : List[Tuple[str, int]], i = 0, j = -1):
        if(tokens[i][0] in ["++", "--", "-", "+", "!", "~", "*", "&", "sizeof"]):
            new_tree = SyntaxTree(SyntaxTree.EXPRESSION, tokens[i][0]+"_pre")
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
    def _parse_multiplicative(self, tokens : List[Tuple[str, int]], i = 0, j = -1):
        operator_location = self._last_outside_parenthesis(tokens, ["*", "/"], i, j)
        if(operator_location != -1 and operator_location != i):
            new_tree = SyntaxTree(SyntaxTree.EXPRESSION, tokens[operator_location][0])
            new_tree.children = [
                self._parse_multiplicative(tokens, i, operator_location),
                self._parse_pointer_to_member(tokens, operator_location+1, j)
            ]
            return new_tree

        return self._parse_pointer_to_member(tokens, i, j)
    
    def _parse_additive(self, tokens : List[Tuple[str, int]], i = 0, j = -1):
        operator_location = self._last_outside_parenthesis(tokens, ["+", "-"], i, j)

        if(operator_location != -1 and operator_location != i):
            new_tree = SyntaxTree(SyntaxTree.EXPRESSION, tokens[operator_location][0])
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
    
    def _parse_logical_or(self, tokens : List[Tuple[str, int]], i = 0, j = -1):
        operator_location = self._last_outside_parenthesis(tokens, ["||"], i, j)
        if(operator_location != -1):
            if(operator_location == i): 
                raise SyntaxError()
            new_tree = SyntaxTree(SyntaxTree.EXPRESSION, tokens[operator_location][0])
            new_tree.children = [
                self._parse_logical_or(tokens, i, operator_location),
                self._parse_logical_and(tokens, operator_location+1, j)
            ]
            return new_tree

        return self._parse_logical_and(tokens, i, j)
    
    def _parse_conditional(self, tokens : List[Tuple[str, int]], i = 0, j = -1) -> Tuple[SyntaxTree, Tuple[int, int]]:
        
        ternary_operator_location = self._first_outside_parenthesis(tokens, ["?"], i, j)
        if(ternary_operator_location != -1):
            ternary_tree = SyntaxTree(SyntaxTree.EXPRESSION, "?")
            tree = self._parse_logical_or(tokens, i, ternary_operator_location)
            ternary_operator_else_location = self._first_outside_parenthesis(tokens, [":"], ternary_operator_location, j)
            ternary_tree.children.append(tree)
            tree = self._parse_expression(tokens, ternary_operator_location + 1, ternary_operator_else_location)

            if(ternary_operator_else_location == -1):
                raise SyntaxError()

            ternary_tree.children.append(tree)
            tree = self._parse_conditional(tokens, ternary_operator_else_location + 1, j)

            ternary_tree.children.append(tree)
            return ternary_tree

        return self._parse_logical_or(tokens, i, j)

    def _parse_expression(self, tokens : List[Tuple[str, int]], i = 0, j = -1):
        return self._parse_assignment(tokens, i, j)
    
    def _parse_assignment(self, tokens : List[Tuple[str, int]], i = 0, j = -1):
        operator_location = self._first_outside_parenthesis(tokens, ["=", "+=", "-=", "*=", "/=", "~=", ">>=", "<<=", "^=", "%=", "&=", "|="], i, j)
        if(operator_location != -1 and operator_location != j-1):
            new_tree = SyntaxTree(SyntaxTree.EXPRESSION, tokens[operator_location][0])
            new_tree.children = [
                self._parse_unary(tokens, i, operator_location),
                self._parse_assignment(tokens, operator_location+1, j)
            ]
            return new_tree

        return self._parse_conditional(tokens, i, j)

    def _analyze(self, tokens : List[Tuple[str, int]], i = 0):
        if(tokens[i][1] == LexicalAnalyzer.KEYWORD):
            if(tokens[i][0] == "if"):
                pass

    # def _parse_statement(self, tokens : List[Tuple[str, int]], i = 0, j = 0):


    def analyze(self, tokens : list[tuple[str, int]]):
        j = 0
        for i, (token, _) in enumerate(tokens):
            if(token == ";"):
                j = i

        return self._parse_expression(tokens, 0, j)


class SemanticAnalyzer():

    def __init__(self):
        self.global_scope = {}
        # self.local_scope = {}


    def get_type(self, tree: SyntaxTree):
        type_definitions = {
            "*_pre" : [("int", ["int*"])],
            "&_pre" : [("int*", ["int"])],

            "+" : [("int", ["int", "int"])],
            "+_pre" : [("int", ["int"])],
            "-_pre": [("int", ["int"])],
            "-" : [("int", ["int", "int"])],
            "*" : [("int", ["int", "int"])],
            "/" : [("int", ["int", "int"])],
            "%" : [("int", ["int", "int"])],

            "++" : [("int", ["int"]), ("int*", ["int*"])],
            "--" : [("int", ["int"]), ("int*", ["int*"])],

            "++_pre" : [("int", ["int"]), ("int*", ["int*"])],
            "--_pre" : [("int", ["int"]), ("int*", ["int*"])],

            "=" : [("int", ["int", "int"])],
            "+=" : [("int", ["int", "int"])],
            "-=" : [("int", ["int", "int"])],
            "*=" : [("int", ["int", "int"])],
            "/=" : [("int", ["int", "int"])],
            "%=" : [("int", ["int", "int"])],
            "&=" : [("int", ["int", "int"])],
            "|=" : [("int", ["int", "int"])],
            "^=" : [("int", ["int", "int"])],
            "+=" : [("int", ["int", "int"])],
            ">>=" : [("int", ["int", "int"])],
            "<<=" : [("int", ["int", "int"])],

            # ":=",
            # "+=",
            "==" : [("bool", ["int", "int"])],
            "!=" : [("bool", ["int", "int"])],
            "<=" : [("bool", ["int", "int"])],
            ">=" : [("bool", ["int", "int"])],
            "<" : [("bool", ["int", "int"])],
            ">" : [("bool", ["int", "int"])],
            "<=>" : [("int", ["int", "int"])],
            "&" : [("int", ["int", "int"])],
            "|" : [("int", ["int", "int"])],
            "^" : [("int", ["int", "int"])],
            "~" : [("int", ["int", "int"])],
            "<<" : [("int", ["int", "int"])],
            ">>" : [("int", ["int", "int"])],
            "!" : [("bool", ["int",])],
            "&&" : [("bool", ["int", "int"])],
            "||" : [("bool", ["int", "int"])],
        }

        if(tree.type == SyntaxTree.NUMERIC_LITERAL):
            tree.data_type = "int"
            return "int"
        
        if(tree.type == SyntaxTree.IDENTIFIER):
            if(tree.expression_type in self.global_scope):
                tree.data_type = self.global_scope[tree.expression_type]
                return self.global_scope[tree.expression_type]
            
            raise SyntaxError(f"Unknown Identifier \"{tree.expression_type}\"")
        
        if(tree.type == SyntaxTree.EXPRESSION):
            if(tree.expression_type == "?"):
                arg_types = [ self.get_type(child) for child in tree.children ]
                if(arg_types[0] != "bool" or arg_types[1] != arg_types[2]):
                    raise SyntaxError(f"Invalid types for ternary operator")
                tree.data_type = arg_types[1]
                return arg_types[1]
            if(tree.expression_type in type_definitions):
                definitions = type_definitions[tree.expression_type]
                arg_types = [ self.get_type(child) for child in tree.children ]
                for return_type, parameter_types in definitions:
                    if(parameter_types == arg_types):
                        tree.data_type = return_type
                        return return_type
                raise SyntaxError(f"Unknown operation \"{tree.expression_type}\" between type {arg_types}")
        
    
    def analyze(self, tree: SyntaxTree):
        self.get_type(tree)

class ASMOperand:
    RESULT_REGISTER_INDEX = 0


    # REGISTER_VALUE

    RESULT_REGISTER = 0
    OPERAND_REGISTER_1 = 1
    OPERAND_REGISTER_2 = 2
    R_VALUE_ADDRESS = 3

#     def __init__(self, index = 0, type = 0):
#         self.index = index
#         self.type = type

class IntermediateCodeGenerator:
    def __init__(self):
        self.global_scope = {}

        self.current_temp_register = 0
        self.current_branch_target = 0

        self.intermediate = []
    
    def _get_next_temp_register(self):
        a = self.current_temp_register
        self.current_temp_register += 1
        return f"t{a}"
    
    def _get_next_branch_target(self):
        a = self.current_branch_target
        self.current_branch_target += 1
        return f"b{a}"
    
    def _emit_code(self, op: str, operands: Tuple[str,str,str]):
        self.intermediate.append((op, operands))

    def _get_emitted(self, template, result_register, operand_registers, r_value_register):
        registers = [result_register] + operand_registers + [r_value_register]
        # print(template)
        return [
            (op, tuple([registers[arg] if arg is not None else "" for arg in args ])) for op, args in template
        ]

    def generate(self, tree: SyntaxTree):

        type_definitions = {
            "*_pre" : [([("ld", (ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_1, None))], ["int*"])],
            # "&_pre" : [("int*", ["int"])],

            "+" : [([("add", (ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_1, ASMOperand.OPERAND_REGISTER_2))], ["int", "int"])],
            "+_pre" : [([], ["int"])],
            "-_pre": [([("neg", (ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_1, None))], ["int"])],
            "-" : [([("sub", (ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_1, ASMOperand.OPERAND_REGISTER_2))], ["int", "int"])],
            "*" : [([("mul", (ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_1, ASMOperand.OPERAND_REGISTER_2))], ["int", "int"])],
            "/" : [([("div", (ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_1, ASMOperand.OPERAND_REGISTER_2))], ["int", "int"])],
            "%" : [([("mod", (ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_1, ASMOperand.OPERAND_REGISTER_2))], ["int", "int"])],

            "++" : [([
                ("mov", (ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_1, None)), 
                ("inc", (ASMOperand.OPERAND_REGISTER_1, None, None)), 
                ("st", (ASMOperand.OPERAND_REGISTER_1, ASMOperand.R_VALUE_ADDRESS, None))
            ], ["int"]), ([
                ("mov", (ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_1, None)), 
                ("inc", (ASMOperand.OPERAND_REGISTER_1, None, None)), 
                ("st", (ASMOperand.OPERAND_REGISTER_1, ASMOperand.R_VALUE_ADDRESS, None))
            ], ["int*"])],
            "--" : [([
                ("mov", (ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_1, None)), 
                ("dev", (ASMOperand.OPERAND_REGISTER_1, None, None)), 
                ("st", (ASMOperand.OPERAND_REGISTER_1, ASMOperand.R_VALUE_ADDRESS, None))
            ], ["int"]), ([
                ("mov", (ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_1, None)), 
                ("dev", (ASMOperand.OPERAND_REGISTER_1, None, None)), 
                ("st", (ASMOperand.OPERAND_REGISTER_1, ASMOperand.R_VALUE_ADDRESS, None))
            ], ["int*"])],

            "++_pre" : [([
                ("inc", (ASMOperand.OPERAND_REGISTER_1, None, None)), 
                ("mov", (ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_1, None)), 
                ("st", (ASMOperand.OPERAND_REGISTER_1, ASMOperand.R_VALUE_ADDRESS, None))
            ], ["int"]), ([
                ("inc", (ASMOperand.OPERAND_REGISTER_1, None, None)), 
                ("mov", (ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_1, None)), 
                ("st", (ASMOperand.OPERAND_REGISTER_1, ASMOperand.R_VALUE_ADDRESS, None))
            ], ["int*"])],
            "--_pre" : [([
                ("dec", (ASMOperand.OPERAND_REGISTER_1, None, None)), 
                ("mov", (ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_1, None)), 
                ("st", (ASMOperand.OPERAND_REGISTER_1, ASMOperand.R_VALUE_ADDRESS, None))
            ], ["int"]), ([
                ("dec", (ASMOperand.OPERAND_REGISTER_1, None, None)), 
                ("mov", (ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_1, None)), 
                ("st", (ASMOperand.OPERAND_REGISTER_1, ASMOperand.R_VALUE_ADDRESS, None))
            ], ["int*"])],

            "=" : [([
                ("mov", (ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_2, None)),
                ("st", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None))
            ], ["int", "int"])],
            "+=" : [([
                ("ld", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None)),
                ("add", (ASMOperand.RESULT_REGISTER, ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_2)),
                ("st", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None))
            ], ["int", "int"])],
            "-=" : [([
                ("ld", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None)),
                ("sub", (ASMOperand.RESULT_REGISTER, ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_2)),
                ("st", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None))
            ], ["int", "int"])],
            "*=" : [([
                ("ld", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None)),
                ("mul", (ASMOperand.RESULT_REGISTER, ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_2)),
                ("st", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None))
            ], ["int", "int"])],
            "/=" : [([
                ("ld", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None)),
                ("div", (ASMOperand.RESULT_REGISTER, ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_2)),
                ("st", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None))
            ], ["int", "int"])],
            "%=" : [([
                ("ld", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None)),
                ("mod", (ASMOperand.RESULT_REGISTER, ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_2)),
                ("st", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None))
            ], ["int", "int"])],
            "&=" : [([
                ("ld", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None)),
                ("and", (ASMOperand.RESULT_REGISTER, ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_2)),
                ("st", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None))
            ], ["int", "int"])],
            "|=" : [([
                ("ld", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None)),
                ("or", (ASMOperand.RESULT_REGISTER, ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_2)),
                ("st", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None))
            ], ["int", "int"])],
            "^=" : [([
                ("ld", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None)),
                ("xor", (ASMOperand.RESULT_REGISTER, ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_2)),
                ("st", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None))
            ], ["int", "int"])],
            ">>=" : [([
                ("ld", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None)),
                ("shr", (ASMOperand.RESULT_REGISTER, ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_2)),
                ("st", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None))
            ], ["int", "int"])],
            "<<=" : [([
                ("ld", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None)),
                ("shl", (ASMOperand.RESULT_REGISTER, ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_2)),
                ("st", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None))
            ], ["int", "int"])],

            # ":=",
            # "+=",
            # "==" : [("bool", ["int", "int"])],
            # "!=" : [("bool", ["int", "int"])],
            # "<=" : [("bool", ["int", "int"])],
            # ">=" : [("bool", ["int", "int"])],
            # "<" : [("bool", ["int", "int"])],
            # ">" : [("bool", ["int", "int"])],
            # "<=>" : [("int", ["int", "int"])],
            "&" : [([
                ("and", (ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_1, ASMOperand.OPERAND_REGISTER_2))
            ], ["int", "int"])],
            # "|" : [("int", ["int", "int"])],
            # "^" : [("int", ["int", "int"])],
            # "~" : [("int", ["int", "int"])],
            # "<<" : [("int", ["int", "int"])],
            ">>" : [([
                ("shr", (ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_1, ASMOperand.OPERAND_REGISTER_2)),
            ], ["int", "int"])],
            # "!" : [("bool", ["int",])],
            # "&&" : [("bool", ["int", "int"])],
            # "||" : [("bool", ["int", "int"])],
        }

        if(tree.type == SyntaxTree.NUMERIC_LITERAL):
            reg = self._get_next_temp_register()
            return [(
                "ldi", (reg, tree.expression_type, "")
            )], reg, reg
        
        if(tree.type == SyntaxTree.IDENTIFIER):
            if(tree.expression_type in self.global_scope):
                reg = self._get_next_temp_register()
                return [("ld", (reg, f"[{tree.expression_type}]", ""))], reg, f"[{tree.expression_type}]"
        if(tree.type == SyntaxTree.EXPRESSION):
            if(tree.expression_type == "?"):
                condition, T, F = [ self.generate(child) for child in tree.children ]
                branch_target = self._get_next_branch_target()
                branch_target_else = self._get_next_branch_target()
                reg = self._get_next_temp_register()
                # print(T, F)
                return condition[0] + [
                    ("bz", (condition[1], branch_target), "")
                ] + T[0] + [
                    ("mov", (reg, T[1], "")),
                    ("j", (branch_target_else, "", "")),
                    ("label", (branch_target, "", ""))
                ] + F[0] + [
                    ("mov", (reg, F[1], "")),
                    ("label", (branch_target_else, "", ""))
                ], reg, reg

            if(tree.expression_type in type_definitions):
                definitions = type_definitions[tree.expression_type]
                arg_types = [ child.data_type for child in tree.children ]
                generated = [ self.generate(child) for child in tree.children ]
                for emitted_template, parameter_types in definitions:
                    if(parameter_types == arg_types):
                        result_register = self._get_next_temp_register()
                    
                        return list(itertools.chain(*[ i[0] for i in generated])) + self._get_emitted(emitted_template, result_register, [
                            generated[0][1], generated[1][1] if len(generated) == 2 else ""
                        ], generated[0][2] if len(generated) >= 1 else ""), result_register, ""



class IntermediateCodeGeneratorOptimizer:

    def __init__(self):
        pass

    def optimize(self, code):
        last_updated = {

        }

        previously_loaded = {

        }

        register_substitutions = {

        }

        out = []

        for i, inst in enumerate(code):
            op = inst[0]
            args = [ arg if arg not in register_substitutions else register_substitutions[arg] for arg in inst[1] ]
            reemit = True
            if(op != "st"):
                last_updated[args[0]] = i

            if(op == "ld"):
                if(args[1] in previously_loaded):
                    previously_loaded_register, previously_loaded_time = previously_loaded[args[1]]
                    if(last_updated[previously_loaded_register] == previously_loaded_time):
                        register_substitutions[args[0]] = previously_loaded_register
                        reemit = False
            if(op == "ld" or op == "st"):
                previously_loaded[args[1]] = (args[0], i)
            
            if(reemit):
                out.append(
                    (op, args)
                )
                

        print(previously_loaded)
        return out


class FinalAssemblyGenerator:

    def generate(self, code):
        s = ",\t"
        return [
            f"\t{i[0]}\t{s.join(i[1])}" if i[0] != "label" else f"{i[1][0]}:"
            for i in code
        ]




if __name__ == "__main__":
    print("--------- Lexer ---------")
    lexer = LexicalAnalyzer()
    text = """result = (x += y * (z >> 2)) & ((flag ? *p++ : -q) & 0xFF);"""
    # text = """(x + y * (z >> 2)) & ((flag ? *p++ : -q) & 0xFF)"""
    # text = """a + (b * c)"""
    # text = "flag ? *p++ : -q"
    # text = """*p++"""
    # text = """1+1+2"""
    tokens = lexer.analyze(text)

    syn = SyntaticAnalyzer()

    print("--------- Syntactic Analysis ---------")
    tree = syn.analyze(tokens)
    print(tree)

    semantic = SemanticAnalyzer()
    semantic.global_scope = {
        "result" : "int",
        "x" : "int",
        "y" : "int",
        "z" : "int",
        "flag" : "bool",
        "p" : "int*",
        "q" : "int",
    }
    print("--------- Semantic Analysis ---------")

    semantic.analyze(tree)

    print("Passed semantic analysis")

    gen = IntermediateCodeGenerator()
    gen.global_scope = {
        "result" : "int",
        "x" : "int",
        "y" : "int",
        "z" : "int",
        "flag" : "bool",
        "p" : "int*",
        "q" : "int",
    }

    generated = gen.generate(tree)[0]

    s = ",\t"
    print("--------- Intermediate Code ---------")
    print("\n".join([ f"{i[0]}\t{s.join(i[1])}" for i in generated]))
    print("--------- Optimized Code ---------")
    optimizer = IntermediateCodeGeneratorOptimizer()
    optimized = optimizer.optimize(generated)
    print("\n".join([ f"{i[0]}\t{s.join(i[1])}" for i in optimized]))
    print("------------ Final --------------")
    final_gen = FinalAssemblyGenerator()
    print("\n".join(final_gen.generate(optimized)))
    


