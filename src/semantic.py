from syntax import SyntaxTree, CType
from errors import CompilationError, CompilerSyntaxError
from c_lib import CLib


class FunctionParameters:
    
    def __init__(self):
        self.stack_memory_allocation : int = 16
        self.declared_variables = {}
        
    def allocate(self, size=8):
        self.stack_memory_allocation += size
    
    def declare_variable(self, name:str, size=8):
        self.stack_memory_allocation += size
        self.declared_variables[name] = StackPosition(self, self.stack_memory_allocation)


class StackPosition:
    def __init__(self, function_parameter:FunctionParameters, offset_from_top:int = 0):
        self.function_parameter = function_parameter
        self.offset_from_top = offset_from_top
    
    def get_offset(self):
        return self.function_parameter.stack_memory_allocation - self.offset_from_top

class SemanticAnalyzer():

    def __init__(self):
        self.global_scope = {}


    def get_type(self, tree: SyntaxTree, local_scope: dict[str, CType]={}, function_parameters:FunctionParameters=None) -> CType | None:
        if(tree.type == SyntaxTree.NUMERIC_LITERAL):
            tree.data_type = "int"
            return CType("int")
        
        if(tree.type == SyntaxTree.IDENTIFIER):
            if(tree.identifier in local_scope):
                tree.data_type = local_scope[tree.identifier]
                return local_scope[tree.identifier]
            if(tree.identifier in self.global_scope):
                tree.data_type = self.global_scope[tree.identifier]
                return self.global_scope[tree.identifier]
            
            raise CompilerSyntaxError(f"Unknown Identifier \"{tree.identifier}\"", tree.line)
        
        if(tree.type == SyntaxTree.EXPRESSION):
            if(tree.expression_type == "?"):
                arg_types = [ self.get_type(child, local_scope, function_parameters) for child in tree.children ]
                if(arg_types[0] != "bool" or arg_types[1] != arg_types[2]):
                    raise CompilerSyntaxError(f"Invalid types for ternary operator", {tree.line})
                tree.data_type = arg_types[1]
                return arg_types[1]
            
            if(tree.expression_type == "*_pre"):
                operand = self.get_type(tree.children[0], local_scope, function_parameters)
                if(operand.pointer_count < 1):
                    raise CompilerSyntaxError(f"Cannot dereference non-pointer type {operand.base}", tree.line)
                tree.data_type = CType(operand.base, operand.pointer_count - 1)
                return tree.data_type
            if(tree.expression_type == "&_pre"):
                operand = self.get_type(tree.children[0], local_scope, function_parameters)
                tree.data_type = CType(operand.base, operand.pointer_count + 1)
                return tree.data_type
            
            if(tree.expression_type == "[]"):
                array_type = self.get_type(tree.children[0], local_scope, function_parameters)
                index_type = self.get_type(tree.children[1], local_scope, function_parameters)
                if(index_type.base != "int" or index_type.pointer_count != 0):
                    raise CompilerSyntaxError(f"Array index must be of type int, got {index_type.base}", tree.line)
                if(array_type.pointer_count < 1):
                    raise CompilerSyntaxError(f"Cannot index non-pointer type {array_type.base}", tree.line)
                tree.data_type = CType(array_type.base, array_type.pointer_count - 1)
                return tree.data_type
            print("Expression operation:", tree.expression_type)
            arg_types = [ self.get_type(child, local_scope, function_parameters) for child in tree.children ]
            print("Argument types:", arg_types)
            return_type = CLib.get_operation_return_type(tree.expression_type, arg_types)
            if(return_type is not None):
                tree.data_type = return_type
                return return_type
            raise CompilerSyntaxError(f"Unknown operation \"{tree.expression_type}\" between type {arg_types} at line {tree.line}")
            # raise CompilerSyntaxError(f"Unknown operation \"{tree.expression_type}\" between type {arg_types} at line {tree.line}")
        
        if(tree.type == SyntaxTree.WHILE_STATEMENT):
            [ self.get_type(child, local_scope, function_parameters) for child in tree.children ]
            # condition_type = self.get_type(tree.children[0], local_scope)
            # self.get_type(tree.children[1], local_scope)
            return "void"

        if(tree.type == SyntaxTree.FOR_STATEMENT):
            [ self.get_type(child, local_scope, function_parameters) for child in tree.children ]
            # self.get_type(tree.children[0], local_scope)
            # condition_type = self.get_type(tree.children[1], local_scope)
            # self.get_type(tree.children[2], local_scope)
            # self.get_type(tree.children[3], local_scope)
            return "void"
        
        # if(tree.type == SyntaxTree.FUNCTION_DECLARATION):
        #     for child in tree.children:
        #         self.get_type(child, local_scope)
        #     return "void"
        
        if(tree.type == SyntaxTree.VARIABLE_DECLARATION):
            if(function_parameters != None):
                local_scope[tree.identifier] = tree.declared_type
                function_parameters.declare_variable(tree.identifier, 8)
            else:
                self.global_scope[tree.identifier] = tree.declared_type
            
            return "void"

        if(tree.type == SyntaxTree.BLOCK_STATEMENT):
            local_scope = local_scope.copy()
            for child in tree.children:
                self.get_type(child, local_scope, function_parameters)
            return "void"
        
        if(tree.type == SyntaxTree.EXTERNAL_BLOCK):
            for child in tree.children:
                self.get_type(child, local_scope, function_parameters)
            return "void"
        
        if(tree.type == SyntaxTree.FUNCTION_DEFINITION):
            local_scope = local_scope.copy()
            for param in tree.parameters:
                local_scope[param.identifier] = param.declared_type
            tree.function_parameters = FunctionParameters()
            self.get_type(tree.body, local_scope, tree.function_parameters)
            return "void"
        
        
        
        

    def analyze(self, tree: SyntaxTree):
        self.get_type(tree)
