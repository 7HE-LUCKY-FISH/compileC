from syntax import CType

class CLib:
    UNARY_OPERATIONS = [
            "+_pre",
            "-_pre",

            "++",
            "--",

            "++_pre",
            "--_pre",

        ]

    ASSIGNMENT_OPERATIONS = [
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
    ]

    BINARY_OPERATIONS = [
        "+", 
        "-", 
        "*", 
        "/", 
        "%", 

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
        "!",
        "&&",
        "||",
        "<<",
        ">>",
        "!",
        "&&",
        "||",
    ]

    @staticmethod
    def get_operation_return_type(op: str, operands: list[CType]) -> CType | None:
        print("Getting operation return type for:", op, operands)
        if op in CLib.UNARY_OPERATIONS:
            if len(operands) != 1:
                return None
            return operands[0]
        if op in CLib.ASSIGNMENT_OPERATIONS:
            if len(operands) != 2:
                return None
            if(operands[0].base != operands[1].base or operands[0].pointer_count != operands[1].pointer_count):
                return None
            return operands[0]
        if op in CLib.BINARY_OPERATIONS:
            if len(operands) != 2:
                return None
            if(operands[0].base != operands[1].base or operands[0].pointer_count != operands[1].pointer_count):
                return None
            return operands[0]
        
        print("Unknown operation:", op)
        return None
        