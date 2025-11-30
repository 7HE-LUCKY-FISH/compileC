from lexer import LexicalAnalyzer
from icode import IntermediateCodeGenerator, IntermediateCodeGeneratorOptimizer, FinalAssemblyGenerator
from syntax import SyntaticAnalyzer
from semantic import SemanticAnalyzer
from errors import CompilationError    




if __name__ == "__main__":
        print("--------- Lexer ---------")
        lexer = LexicalAnalyzer()
#         text = """
# nt(*abc=1+1,2+2,3+3,4+4,dsfa==s,&(*333))
# """
#         text = """
# &(*333)
# """
        text = """
int *****a = 0,b(int)
"""
        tokens = lexer.analyze(text)

        syn = SyntaticAnalyzer(tokens)

        print("--------- Syntactic Analysis ---------")
        # tree = syn._parse_expression_list(0, len(tokens))
        # print(tree)
        print(syn.parenthesis_skip_list)
        print(syn._parse_declaration(0, len(tokens)))