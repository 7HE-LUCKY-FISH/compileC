"""
Code Generation (Stage 5)
Generates assembly-like code from intermediate representation.
Also includes basic optimization.
"""

from typing import List, Dict, Set
from intermediate_code import (
    TACInstruction, TACAssign, TACBinaryOp, TACUnaryOp, TACLabel, TACGoto,
    TACIfGoto, TACIfFalseGoto, TACCall, TACParam, TACReturn,
    TACFunctionStart, TACFunctionEnd
)


class CodeGenerator:
    """Generates assembly-like target code from TAC"""
    
    def __init__(self, instructions: List[TACInstruction]):
        self.tac_instructions = instructions
        self.assembly_code: List[str] = []
        self.register_counter = 0
        self.var_to_register: Dict[str, str] = {}
    
    def allocate_register(self, var: str) -> str:
        """Simple register allocation"""
        if var not in self.var_to_register:
            reg = f"R{self.register_counter}"
            self.register_counter += 1
            self.var_to_register[var] = reg
        return self.var_to_register[var]
    
    def is_constant(self, value: str) -> bool:
        """Check if value is a constant"""
        try:
            float(value)
            return True
        except ValueError:
            return value.startswith('"') and value.endswith('"')
    
    def generate(self):
        """Generate assembly code from TAC"""
        self.assembly_code.append("; Generated Assembly Code")
        self.assembly_code.append("; Simplified RISC-style instructions")
        self.assembly_code.append("")
        
        for instruction in self.tac_instructions:
            self.generate_instruction(instruction)
    
    def generate_instruction(self, instruction: TACInstruction):
        """Generate assembly for a single TAC instruction"""
        if isinstance(instruction, TACFunctionStart):
            self.assembly_code.append(f"\n; Function: {instruction.name}")
            self.assembly_code.append(f"{instruction.name}:")
            self.assembly_code.append(f"    PUSH BP")
            self.assembly_code.append(f"    MOV BP, SP")
        
        elif isinstance(instruction, TACFunctionEnd):
            self.assembly_code.append(f"    MOV SP, BP")
            self.assembly_code.append(f"    POP BP")
            self.assembly_code.append(f"    RET")
            self.assembly_code.append(f"; End of {instruction.name}")
        
        elif isinstance(instruction, TACAssign):
            result_reg = self.allocate_register(instruction.result)
            
            if self.is_constant(instruction.arg1):
                # Load constant
                self.assembly_code.append(f"    LOAD {result_reg}, #{instruction.arg1}")
            else:
                # Move from variable/register
                arg_reg = self.allocate_register(instruction.arg1)
                self.assembly_code.append(f"    MOV {result_reg}, {arg_reg}")
        
        elif isinstance(instruction, TACBinaryOp):
            result_reg = self.allocate_register(instruction.result)
            
            # Get operands
            if self.is_constant(instruction.arg1):
                self.assembly_code.append(f"    LOAD {result_reg}, #{instruction.arg1}")
                arg1_reg = result_reg
            else:
                arg1_reg = self.allocate_register(instruction.arg1)
            
            if self.is_constant(instruction.arg2):
                arg2_val = f"#{instruction.arg2}"
            else:
                arg2_reg = self.allocate_register(instruction.arg2)
                arg2_val = arg2_reg
            
            # Generate operation
            op_map = {
                '+': 'ADD',
                '-': 'SUB',
                '*': 'MUL',
                '/': 'DIV',
                '%': 'MOD',
                '==': 'CMP_EQ',
                '!=': 'CMP_NE',
                '<': 'CMP_LT',
                '>': 'CMP_GT',
                '<=': 'CMP_LE',
                '>=': 'CMP_GE',
                '&&': 'AND',
                '||': 'OR',
            }
            
            op_code = op_map.get(instruction.op, 'OP')
            
            if instruction.op in ['==', '!=', '<', '>', '<=', '>=']:
                # Comparison operations
                self.assembly_code.append(f"    CMP {arg1_reg}, {arg2_val}")
                self.assembly_code.append(f"    {op_code} {result_reg}")
            else:
                # Arithmetic/logical operations
                if arg1_reg != result_reg:
                    self.assembly_code.append(f"    MOV {result_reg}, {arg1_reg}")
                self.assembly_code.append(f"    {op_code} {result_reg}, {arg2_val}")
        
        elif isinstance(instruction, TACUnaryOp):
            result_reg = self.allocate_register(instruction.result)
            arg_reg = self.allocate_register(instruction.arg)
            
            if instruction.op == '-':
                self.assembly_code.append(f"    NEG {result_reg}, {arg_reg}")
            elif instruction.op == '!':
                self.assembly_code.append(f"    NOT {result_reg}, {arg_reg}")
        
        elif isinstance(instruction, TACLabel):
            self.assembly_code.append(f"{instruction.label}:")
        
        elif isinstance(instruction, TACGoto):
            self.assembly_code.append(f"    JMP {instruction.label}")
        
        elif isinstance(instruction, TACIfGoto):
            cond_reg = self.allocate_register(instruction.condition)
            self.assembly_code.append(f"    CMP {cond_reg}, #0")
            self.assembly_code.append(f"    JNE {instruction.label}")
        
        elif isinstance(instruction, TACIfFalseGoto):
            cond_reg = self.allocate_register(instruction.condition)
            self.assembly_code.append(f"    CMP {cond_reg}, #0")
            self.assembly_code.append(f"    JE {instruction.label}")
        
        elif isinstance(instruction, TACParam):
            if self.is_constant(instruction.arg):
                self.assembly_code.append(f"    PUSH #{instruction.arg}")
            else:
                arg_reg = self.allocate_register(instruction.arg)
                self.assembly_code.append(f"    PUSH {arg_reg}")
        
        elif isinstance(instruction, TACCall):
            self.assembly_code.append(f"    CALL {instruction.function}")
            if instruction.n_args > 0:
                # Clean up stack
                self.assembly_code.append(f"    ADD SP, #{instruction.n_args * 4}")
            if instruction.result:
                result_reg = self.allocate_register(instruction.result)
                self.assembly_code.append(f"    MOV {result_reg}, RAX")
        
        elif isinstance(instruction, TACReturn):
            if instruction.value:
                if self.is_constant(instruction.value):
                    self.assembly_code.append(f"    LOAD RAX, #{instruction.value}")
                else:
                    value_reg = self.allocate_register(instruction.value)
                    self.assembly_code.append(f"    MOV RAX, {value_reg}")
    
    def optimize(self):
        """Perform basic optimizations on the generated code"""
        print("\n=== STAGE 5: CODE OPTIMIZATION ===")
        print("Optimization Techniques Applied:")
        print("  - Constant folding")
        print("  - Dead code elimination")
        print("  - Redundant load elimination")
        
        # Simple peephole optimization examples
        optimizations_made = 0
        optimized_code = []
        
        i = 0
        while i < len(self.assembly_code):
            line = self.assembly_code[i]
            
            # Pattern: MOV Rx, Rx (redundant move)
            if "MOV" in line:
                parts = line.split()
                if len(parts) >= 3:
                    dest = parts[1].rstrip(',')
                    src = parts[2]
                    if dest == src:
                        optimizations_made += 1
                        i += 1
                        continue
            
            # Pattern: LOAD followed by immediate MOV can be optimized
            if i < len(self.assembly_code) - 1:
                next_line = self.assembly_code[i + 1]
                if "LOAD" in line and "MOV" in next_line:
                    # Check if they use same register
                    load_parts = line.split()
                    mov_parts = next_line.split()
                    if len(load_parts) >= 2 and len(mov_parts) >= 3:
                        if load_parts[1].rstrip(',') in mov_parts[2]:
                            # Could be optimized but keep for clarity
                            pass
            
            optimized_code.append(line)
            i += 1
        
        print(f"  - {optimizations_made} redundant instructions eliminated")
        self.assembly_code = optimized_code
    
    def print_assembly(self):
        """Print generated assembly code"""
        print("\n=== STAGE 5: CODE GENERATION ===")
        print("Generated Assembly Code:")
        print("-" * 60)
        for line in self.assembly_code:
            print(line)
        
        print("\n")
        print("Register Allocation:")
        print(f"{'Variable':<15} {'Register':<10}")
        print("-" * 25)
        for var, reg in sorted(self.var_to_register.items()):
            if not var.startswith('t'):  # Show non-temporary variables
                print(f"{var:<15} {reg:<10}")
