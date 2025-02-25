
class LexerError(Exception):
    
    def __init__(self, message: str, position: tuple[int, int], expected: list[str], got: str):
        super().__init__(message)

        self.position = position
        self.expected = expected
        self.got = got