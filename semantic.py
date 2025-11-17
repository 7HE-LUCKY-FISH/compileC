from syntax import SyntaxTree


class SemanticAnalyzer():

    def __init__(self):
        self.global_scope = {}


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
