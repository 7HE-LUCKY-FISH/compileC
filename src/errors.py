from token import Token

class CompilationError(Exception):
    def __init__(self, message, line, token_content:Token=None):
        self.message = message
        self.line = line
        self.token_content = token_content
        super().__init__(self.message)

    def __str__(self):
        token_info = f" near '{self.token_content}'" if self.token_content else ""
        return f"[Line {self.line}] Error{token_info}: {self.message}"
    
class CompilerSyntaxError(CompilationError):
    def __str__(self):
        token_info = f" near '{self.token_content}'" if self.token_content else ""
        return f"[Line {self.line}] Error{token_info}: {self.message}"