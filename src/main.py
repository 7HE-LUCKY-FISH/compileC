from lexer import LexicalAnalyzer
from icode import IntermediateCodeGenerator, IntermediateCodeGeneratorOptimizer, FinalAssemblyGenerator
from syntax import SyntaticAnalyzer
from semantic import SemanticAnalyzer
from errors import CompilationError    



if __name__ == "__main__":
    # try:
        print("--------- Lexer ---------")
        lexer = LexicalAnalyzer()
#         text = """
# int main(int argc, char** argv) {
#     int a = 5;
#     if(a > 0) {
#         a = a - 1;
#     } else {
#         a = a + 1;
#     }
#     return 0;
# }


# """
        text = """
int factorial(int n) {
    if(n == 0) {
        return 1;
    }
    return factorial(n-1) * n;
}
int main(int argc, char** argv) {
    int a = factorial(5);
    return 0;
}


"""
        # text = """result = (x += y * (z >> 2)) & ((flag ? *p++ : -q) & 0xFF);"""
        # text = """(x + y * (z >> 2)) & ((flag ? *p++ : -q) & 0xFF)"""
        # text = """a + (b * c)"""
        # text = "flag ? *p++ : -q"
        # text = """*p++"""
        # text = """1+1+2"""
        #text = """while (x < 10){ x = x + 1; }"""
        
        #text = """for (int i = 0 i < 10 i++)  { x = x + 1; }"""
        tokens = lexer.analyze(text)

        syn = SyntaticAnalyzer(tokens)

        print("--------- Syntactic Analysis ---------")
        tree = syn.analyze()
        print(tree)

        semantic = SemanticAnalyzer()
        # semantic.global_scope = {
        #     "result" : "int",
        #     "x" : "int",
        #     "y" : "int",
        #     "z" : "int",
        #     "flag" : "bool",
        #     "p" : "int*",
        #     "q" : "int",
        # }
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

        generated = gen.generate(tree)

        s = ",\t"
        print("--------- Intermediate Code ---------")
        print(generated)
        for n, code in generated.items():    
            print("\n".join([ f"{i[0]}\t{s.join(i[1])}" for i in code]))
            print()
        print("--------- Optimized Code ---------")
        optimizer = IntermediateCodeGeneratorOptimizer()
        optimized = []
        for n, code in generated.items():    
            k = optimizer.optimize(code)
            optimized.append(k)
            print("\n".join([ f"{i[0]}\t{s.join(i[1])}" for i in k]))
            print()
        # optimized = optimizer.optimize(generated)
        # print("\n".join([ f"{i[0]}\t{s.join(i[1])}" for i in optimized]))
        print("------------ Final --------------")
        final_gen = FinalAssemblyGenerator()
        full = []
        for k in optimized:
            full += final_gen.generate(k)
        print("\n".join(full))
    # except CompilationError as ce:
    #     print(str(ce))
    # except Exception as e:
    #     print("Unhandled exception:", str(e))