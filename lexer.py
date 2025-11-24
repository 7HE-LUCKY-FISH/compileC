from typing import *
from trie import Trie
from errors import CompilationError

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
        STRING_DELIMETERS = [ '"', "'" ]
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

    def analyze(self, s) -> list[tuple[str, int, int]]:
        i = 0
        n = len(s)
        line = 1
        tokens = []

        while(i < n):


            if s[i].isspace():
                if s[i] == '\n':
                    line += 1
                i += 1
                continue

            typ, j = self._parse_token(s, i)

            if typ is None:
                raise CompilationError(f"Unexpected character '{s[i]}'", line, s[i])
            
            if(typ != None):
                tokens.append((s[i:j], typ, line))
            # Count newlines in the token
            for c in s[i:j]:
                if c == '\n':
                    line += 1
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

        for tk, typ, ln in tokens:
            print(tk, typestr[typ], ln)
        
        return tokens
