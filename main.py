from lexer import LexicalAnalyzer
from icode import IntermediateCodeGenerator, IntermediateCodeGeneratorOptimizer, FinalAssemblyGenerator
from syntax import SyntaticAnalyzer
from semantic import SemanticAnalyzer
    



if __name__ == "__main__":
    print("--------- Lexer ---------")
    lexer = LexicalAnalyzer()
    #text = """result = (x += y * (z >> 2)) & ((flag ? *p++ : -q) & 0xFF);"""
    # text = """(x + y * (z >> 2)) & ((flag ? *p++ : -q) & 0xFF)"""
    # text = """a + (b * c)"""
    # text = "flag ? *p++ : -q"
    # text = """*p++"""
    # text = """1+1+2"""
    text = """while (x < 10) { x = x + 1; }"""
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