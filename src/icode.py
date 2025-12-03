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


        self.function_parameter_registers = [ "x0", "x1", "x2", "x3" ]

        self.stack_size = 0

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
            "*_pre" : [([("ldr", (ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_1, None))], ["int*"])],

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
                ("str", (ASMOperand.OPERAND_REGISTER_1, ASMOperand.R_VALUE_ADDRESS, None))
            ], ["int"]), ([
                ("mov", (ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_1, None)), 
                ("inc", (ASMOperand.OPERAND_REGISTER_1, None, None)), 
                ("str", (ASMOperand.OPERAND_REGISTER_1, ASMOperand.R_VALUE_ADDRESS, None))
            ], ["int*"])],
            "--" : [([
                ("mov", (ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_1, None)), 
                ("dec", (ASMOperand.OPERAND_REGISTER_1, None, None)), 
                ("str", (ASMOperand.OPERAND_REGISTER_1, ASMOperand.R_VALUE_ADDRESS, None))
            ], ["int"]), ([
                ("mov", (ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_1, None)), 
                ("dec", (ASMOperand.OPERAND_REGISTER_1, None, None)), 
                ("str", (ASMOperand.OPERAND_REGISTER_1, ASMOperand.R_VALUE_ADDRESS, None))
            ], ["int*"])],

            "++_pre" : [([
                ("inc", (ASMOperand.OPERAND_REGISTER_1, None, None)), 
                ("mov", (ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_1, None)), 
                ("str", (ASMOperand.OPERAND_REGISTER_1, ASMOperand.R_VALUE_ADDRESS, None))
            ], ["int"]), ([
                ("inc", (ASMOperand.OPERAND_REGISTER_1, None, None)), 
                ("mov", (ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_1, None)), 
                ("str", (ASMOperand.OPERAND_REGISTER_1, ASMOperand.R_VALUE_ADDRESS, None))
            ], ["int*"])],
            "--_pre" : [([
                ("dec", (ASMOperand.OPERAND_REGISTER_1, None, None)), 
                ("mov", (ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_1, None)), 
                ("str", (ASMOperand.OPERAND_REGISTER_1, ASMOperand.R_VALUE_ADDRESS, None))
            ], ["int"]), ([
                ("dec", (ASMOperand.OPERAND_REGISTER_1, None, None)), 
                ("mov", (ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_1, None)), 
                ("str", (ASMOperand.OPERAND_REGISTER_1, ASMOperand.R_VALUE_ADDRESS, None))
            ], ["int*"])],

            "=" : [([
                ("mov", (ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_2, None)),
                ("str", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None))
            ], ["int", "int"])],
            "+=" : [([
                ("ldr", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None)),
                ("add", (ASMOperand.RESULT_REGISTER, ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_2)),
                ("str", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None))
            ], ["int", "int"])],
            "-=" : [([
                ("ldr", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None)),
                ("sub", (ASMOperand.RESULT_REGISTER, ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_2)),
                ("str", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None))
            ], ["int", "int"])],
            "*=" : [([
                ("ldr", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None)),
                ("mul", (ASMOperand.RESULT_REGISTER, ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_2)),
                ("str", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None))
            ], ["int", "int"])],
            "/=" : [([
                ("ldr", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None)),
                ("div", (ASMOperand.RESULT_REGISTER, ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_2)),
                ("str", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None))
            ], ["int", "int"])],
            "%=" : [([
                ("ldr", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None)),
                ("mod", (ASMOperand.RESULT_REGISTER, ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_2)),
                ("str", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None))
            ], ["int", "int"])],
            "&=" : [([
                ("ldr", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None)),
                ("and", (ASMOperand.RESULT_REGISTER, ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_2)),
                ("str", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None))
            ], ["int", "int"])],
            "|=" : [([
                ("ldr", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None)),
                ("or", (ASMOperand.RESULT_REGISTER, ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_2)),
                ("str", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None))
            ], ["int", "int"])],
            "^=" : [([
                ("ldr", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None)),
                ("xor", (ASMOperand.RESULT_REGISTER, ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_2)),
                ("str", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None))
            ], ["int", "int"])],
            ">>=" : [([
                ("ldr", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None)),
                ("shr", (ASMOperand.RESULT_REGISTER, ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_2)),
                ("str", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None))
            ], ["int", "int"])],
            "<<=" : [([
                ("ldr", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None)),
                ("shl", (ASMOperand.RESULT_REGISTER, ASMOperand.RESULT_REGISTER, ASMOperand.OPERAND_REGISTER_2)),
                ("str", (ASMOperand.RESULT_REGISTER, ASMOperand.R_VALUE_ADDRESS, None))
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
                "ldi", (reg, str(tree.expression_type), "")
            )], reg, reg
        
        if(tree.type == SyntaxTree.IDENTIFIER):
            if(tree.value in self.local_scope):
                typ, alloc = self.local_scope[tree.value]
                if(typ == 0):
                    reg = self._get_next_temp_register()
                    return [("ldr", (reg, alloc, ""))], reg, alloc
                elif(typ == 1):
                    return [], alloc, ""

            if(tree.value in self.global_scope):
                reg = self._get_next_temp_register()
                return [("ldr", (reg, f"[{tree.expression_type}]", ""))], reg, f"[{tree.expression_type}]"
        if(tree.type == SyntaxTree.EXPRESSION):

            if(tree.expression_type == "FUNCTION_CALL"):
                parameters = [ self.generate(child) for child in tree.parameters ]


                code = []

                for target_reg, res in zip(self.function_parameter_registers, parameters):
                    c, r, _, = res
                    code += c
                    code += [("mov", (target_reg, r, ""))]
                
                code += [
                    ("bl", (tree.function_name.value, "", ""))
                ]

                return code, "x0", None


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
                arg_types = [ str(child.data_type) for child in tree.children ]
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
            code += [("b", (start_label, "", ""))]
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
            code += [("b", (start_label, "", ""))]
            code += [("label", (end_label, "", ""))]
            
            return code, None, None

        if(tree.type == SyntaxTree.CONDITIONAL_STATEMENT):
            condition = tree.condition
            if_block = tree.if_block
            else_block = tree.else_block

            cond_code, cond_reg, _ = self.generate(condition)
            print(condition)
            if_code, _, _ = self.generate(if_block)

            else_code = []
            if(else_block != None):
                else_code, _, _ = self.generate(else_block)

            else_label = self._get_next_branch_target()
            end_label = self._get_next_branch_target()

            code = []
            code += cond_code
            code += [("bz", (cond_reg, else_label, ""))]
            code += if_code
            code += [("b", (end_label, "", ""))]
            code += [("label", (else_label, "", ""))]
            code += else_code
            code += [("label", (end_label, "", ""))]

            return code, None, None

        if(tree.type == SyntaxTree.RETURN_STATEMENT):
            epilogue = [
                ("ldp", ("x29", "x30", "[sp]")),
                ("add", ("sp", "sp", f"#{self.stack_size}")),
                ("ret", ("", "", ""))
            ]
            c, reg, _ = self.generate(tree.children[0])
            code = []
            code += c
            code += [("mov", ("x0", reg, ""))]
            code += epilogue
            return code, None, None

        if(tree.type == SyntaxTree.BLOCK_STATEMENT):
            code = []
            for child in tree.children:
                c, _, _ = self.generate(child)
                code += c
            return code, None, None

        if(tree.type == SyntaxTree.EXTERNAL_BLOCK):
            code = {}
            for child in tree.children:
                c, _, _ = self.generate(child)
                code[child.identifier] = c
            return code

        if(tree.type == SyntaxTree.VARIABLE_DECLARATION):

            return [], None, None
        
        if(tree.type == SyntaxTree.FUNCTION_DEFINITION):
            self.local_scope = {}
            for var_name, alloc in tree.function_parameters.declared_variables.items():
                self.local_scope[var_name] = (0, f"[sp, #${alloc.get_offset()}]")
            print(self.local_scope)

            for reg_alloc, parameter in zip(self.function_parameter_registers, tree.parameters):
                name, type = parameter
                self.local_scope[name] = (1, reg_alloc) 


            self.stack_size = tree.function_parameters.stack_memory_allocation
            c, _, _ = self.generate(tree.body)

            code = []
            code += [
                ("label", (tree.identifier, "", "")),
                ("sub", ("sp", "sp", f"#{tree.function_parameters.stack_memory_allocation}")),
                ("stp", ("x29", "x30", "[sp]")),
                ("mov", ("x29", "sp", ""))
            ]
            code += c

            return code, None, None
        
        return [], None, None


class DSU:
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = n or [1] or n

    def find(self, x: int):
        if self.parent[x] == x:
            return x
        self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: int, y: int):
        x_parent = self.find(x)
        y_parent = self.find(y)
        if self.rank[x_parent] > self.rank[y_parent]:
            self.parent[y_parent] = x_parent
        else:  # inserted
            if self.rank[x_parent] < self.rank[y_parent]:
                self.parent[x_parent] = y_parent
            else:  # inserted
                self.parent[x_parent] = y_parent
                self.rank[y_parent] = 1

class RegisterDSU:
    def __init__(self, registers: list[str]):
        self.registers = registers
        self.dsu = DSU(len(self.registers))
        self.mapping = {}
        for i, reg in enumerate(self.registers):
            self.mapping[reg] = i

    def union(self, x: str, y: str):
        self.dsu.union(self.mapping[x], self.mapping[y])

    def find(self, x: str):
        return self.registers[self.dsu.find(self.mapping[x])]

    def get_all_equivalencies(self) -> dict[str, str]:
        out = {}
        for i, reg in enumerate(self.registers):
            out[reg] = self.registers[self.dsu.find(i)]
        return out

class IntermediateCodeGeneratorOptimizer:

    def __init__(self):
        pass

    def optimize(self, code):
        out = self._determine_equivalent_registers(code)
        out = self._remove_unused_registers(out)
        out = self._remove_unused_registers(out)
        out = self._remove_unnecessary_load_stores(out)
        return out

    def _remove_unnecessary_load_stores(self, code):
        previously_loaded = {}
        last_updated = {}
        equivalent_registers = {}
        out = []
        for i, inst in enumerate(code):
            op = inst[0]
            args = inst[1]
            reemit = True
            if op!= 'str':
                last_updated[args[0]] = i
            if op == 'ldr':
                if args[1] in previously_loaded:
                    previously_loaded_register, previously_loaded_time = previously_loaded[args[1]]
                    if last_updated[previously_loaded_register] == previously_loaded_time:
                        equivalent_registers[args[0]] = previously_loaded_register
                        reemit = False
            if op == 'ldr' or op == 'str':
                previously_loaded[args[1]] = (args[0], i)
            if reemit:
                out.append((op, args))
        print(previously_loaded, last_updated)
        print(equivalent_registers)
        return self._replace_equivalent_registers(out, equivalent_registers)

    @staticmethod
    def _replace_equivalent_registers(code, equivalent_registers):
        out = []
        for i, inst in enumerate(code):
            op = inst[0]
            args = [arg if arg not in equivalent_registers else equivalent_registers[arg] for arg in inst[1]]
            reemit = True
            if op == 'mov' and args[0] == args[1]:
                reemit = False
            if reemit:
                out.append((op, args))
        return out

    def _determine_equivalent_registers(self, code):
        used_registers = set()
        for i, inst in enumerate(code):
            op = inst[0]
            args = inst[1]
            for i in args:
                if i.startswith('t'):
                    used_registers.add(i)
        dsu = RegisterDSU(list(used_registers))
        for i, inst in enumerate(code):
            op = inst[0]
            args = inst[1]
            if op == 'mov' and args[0].startswith('t') and args[1].startswith('t'):
                dsu.union(args[0], args[1])
        return self._replace_equivalent_registers(code, dsu.get_all_equivalencies())

    def _remove_unused_registers(self, code):
        ARITHMETIC_INSTRUCTIONS = ['add', 'sub', 'mul', 'div', 'mod', 'and', 'or', 'xor', 'shl', 'shr', 'lt', 'gt', 'le', 'ge']
        used_registers = set()
        for i, inst in enumerate(code):
            op = inst[0]
            args = inst[1]
            if op in ARITHMETIC_INSTRUCTIONS:
                for arg in args[1:]:
                    if arg.startswith('t'):
                        used_registers.add(arg)
            if op in ['str'] and args[0].startswith('t'):
                used_registers.add(args[0])
            if op in ['bz'] and args[0].startswith('t'):
                used_registers.add(args[0])
            if op in ['mov'] and args[1].startswith('t'):
                used_registers.add(args[1])
        out = []
        for i, inst in enumerate(code):
            op = inst[0]
            args = inst[1]
            reemit = True
            if op in ARITHMETIC_INSTRUCTIONS and args[0].startswith('t'):
                if args[0] not in used_registers:
                    reemit = False
            if op == 'ldr' and args[0].startswith('t'):
                if args[0] not in used_registers:
                    reemit = False
            if op == 'mov' and args[0].startswith('t'):
                if args[0] not in used_registers:
                    reemit = False
            if reemit:
                out.append((op, args))
        return out



class FinalAssemblyGenerator:
    GENERAL_PURPOSE = ["x0", "x1", "x3", "x4", "x5", "x6", "x7", "x8", "x8", "x9"]

    def generate(self, code):
        usable = set(self.GENERAL_PURPOSE)
        used = set()
        needed = set()

        for inst in code:
            op = inst[0]
            args = inst[1]
            
            for i in args:
                if(i.startswith("x")):
                    used.add(i)
                if(i.startswith("t")):
                    needed.add(i)
        
        usable = usable - used

        register_assignments = {}

        for assigned, temp in zip(usable, needed):
            register_assignments[temp] = assigned
        

        code = IntermediateCodeGeneratorOptimizer._replace_equivalent_registers(code, register_assignments)            

        s = ",\t"
        return [
            f"\t{i[0]}\t{s.join(i[1])}" if i[0] != "label" else f"{i[1][0]}:"
            for i in code
        ]
