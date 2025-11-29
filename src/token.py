class Token:
    def __init__(self, type_ : int, value : str, line : int, index: int):
        self.type = type_
        self.value = value
        self.line = line
        self.index = index

    def __repr__(self):
        return f"Token(type={self.type}, value={self.value}, line={self.line}, index={self.index})"