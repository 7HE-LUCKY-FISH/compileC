import itertools
from typing import *
from syntax import SyntaxTree


class ASMOperand:
    RESULT_REGISTER_INDEX = 0


    # REGISTER_VALUE

    RESULT_REGISTER = 0
    OPERAND_REGISTER_1 = 1
    OPERAND_REGISTER_2 = 2
    R_VALUE_ADDRESS = 3


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
        return [
            (op, tuple([registers[arg] if arg is not None else "" for arg in args ])) for op, args in template
        ]

    def generate(self, tree: SyntaxTree):

        type_definitions = {
            "*_pre" : [([("ld", (ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_1, None))], ["int*"])],

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

            "&" : [([
                ("and", (ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_1, ASMOperand.OPERAND_REGISTER_2))
            ], ["int", "int"])],
            ">>" : [([
                ("shr", (ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_1, ASMOperand.OPERAND_REGISTER_2)),
            ], ["int", "int"])],
            "<" : [([
                ("lt", (ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_1, ASMOperand.OPERAND_REGISTER_2))], 
                ["int", "int"])],
            ">" : [([
                ("gt", (ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_1, ASMOperand.OPERAND_REGISTER_2))], 
                ["int", "int"])],
            "<=" : [([
                ("le", (ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_1, ASMOperand.OPERAND_REGISTER_2))], 
                ["int", "int"])],
            ">=" : [([
                ("ge", (ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_1, ASMOperand.OPERAND_REGISTER_2))],
                  ["int", "int"])],
            "==" : [([
                ("eq", (ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_1, ASMOperand.OPERAND_REGISTER_2))], 
                ["int", "int"])],
            "!=" : [([
                ("ne", (ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_1, ASMOperand.OPERAND_REGISTER_2))], 
                ["int", "int"])],
            "&&" : [([
                ("and", (ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_1, ASMOperand.OPERAND_REGISTER_2))], 
                ["int", "int"])],
            "||" : [([
                ("or", (ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_1, ASMOperand.OPERAND_REGISTER_2))], 
                ["int", "int"])],
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

        if(tree.type == SyntaxTree.WHILE_STATEMENT):
            cond_node = tree.children[0]
            body_node = tree.children[1]
            
            start_label = self._get_next_branch_target()
            end_label = self._get_next_branch_target()
            
            cond_code, cond_reg, _ = self.generate(cond_node)
            body_code, _, _ = self.generate(body_node)
            
            code = [("label", (start_label, "", ""))]
            code += cond_code
            code += [("bz", (cond_reg, end_label, ""))]
            code += body_code
            code += [("j", (start_label, "", ""))]
            code += [("label", (end_label, "", ""))]
            
            return code, None, None

        if(tree.type == SyntaxTree.FOR_STATEMENT):
            init_node = tree.children[0]
            cond_node = tree.children[1]
            update_node = tree.children[2]
            body_node = tree.children[3]
            
            start_label = self._get_next_branch_target()
            end_label = self._get_next_branch_target()
            
            init_code, _, _ = self.generate(init_node)
            cond_code, cond_reg, _ = self.generate(cond_node)
            update_code, _, _ = self.generate(update_node)
            body_code, _, _ = self.generate(body_node)
            
            code = init_code
            code += [("label", (start_label, "", ""))]
            code += cond_code
            code += [("bz", (cond_reg, end_label, ""))]
            code += body_code
            code += update_code
            code += [("j", (start_label, "", ""))]
            code += [("label", (end_label, "", ""))]
            
            return code, None, None

        if(tree.type == SyntaxTree.BLOCK_STATEMENT):
            code = []
            for child in tree.children:
                c, _, _ = self.generate(child)
                code += c
            return code, None, None



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
