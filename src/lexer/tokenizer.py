from enum import Enum

from src.utils.error_utils import LexerError


class TokenType(Enum):
    BEGIN_ARRAY = "["
    END_ARRAY = "]"
    BEGIN_OBJECT = "{"
    END_OBJECT = "}"
    NAME_SEPARATOR = ":"
    VALUE_SEPARATOR = ","
    NULL = "NULL"
    TRUE = "TRUE"
    FALSE = "FALSE"
    STRING = "STRING"
    NUMBER = "NUMBER"
    EOF = "EOF"

class Token:

    def __init__(self, type: TokenType, value: str | None, position: tuple[int, int]):
        self.type = type
        self.value = value
        self.position = position

class TokenizationError(LexerError):
    
    def __init__(self, message: str, position: tuple[int, int], expected: list[TokenType], got: str):
        super().__init__(message, position, [token.value for token in expected], got)

def tokenize(json: str) -> list[Token]:
    tokens: list[Token] = list()
    i: int = 0
    length: int = len(json)
    number_chars: set[chr] = set("0123456789.eE-")

    line: int = 1
    column: int = 0

    while i < length:
        char: chr = json[i]
        column += 1

        if char.isspace():
            i += 1
            continue

        if char == '\n':
            line += 1
            column = 1
            i += 1
            continue

        if char in "{[:]},": 
            tokens.append(Token({
                '{': TokenType.BEGIN_OBJECT,  '[': TokenType.BEGIN_ARRAY,
                '}': TokenType.END_OBJECT,    ']': TokenType.END_ARRAY,
                ':': TokenType.NAME_SEPARATOR, ',': TokenType.VALUE_SEPARATOR
            }[char], None, (line, column)))

            i += 1
            continue

        match char:
            case 'n' if json[i:i+4] == 'null':
                tokens.append(Token(TokenType.NULL, 'null', (line, column)))
                i += 3
                column += 3

            case 't' if json[i:i+4] == 'true':
                tokens.append(Token(TokenType.TRUE, 'true', (line, column)))
                i += 3
                column += 3

            case 'f' if json[i:i+5] == 'false':
                tokens.append(Token(TokenType.FALSE, 'false', (line, column)))
                i += 4
                column += 4

            case '"':
                end_idx: int = json.find('"', i+1)

                if end_idx == -1:
                    raise TokenizationError("Missing closing '\"'", (line, column), [TokenType.STRING], char)

                value: str = json[i+1:end_idx]
                tokens.append(Token(TokenType.STRING, value, (line, column)))
                column += end_idx - i
                i = end_idx

            case _ if char.isdigit() or char == '-':
                end_idx: int = i

                if char == "-" and json[i + 1] == '.':
                    raise TokenizationError(f"Unexpected character in number '{json[i + 1]}'", (line, column), [TokenType.EOF], char)

                while end_idx < length and json[end_idx] in number_chars:
                    end_idx += 1

                value: str = json[i:end_idx]
                
                if not value[-1].isdigit():
                    raise TokenizationError(f"Unexpected character in number '{value[-1]}'", (line, column), [TokenType.EOF], char)
                
                tokens.append(Token(TokenType.NUMBER, value, (line, column)))
                column += end_idx - i - 1
                i = end_idx - 1

            case _:
                raise TokenizationError(f"Unexpected character in number '{char}'", (line, column), [t for t in TokenType], char)
        i += 1

    return tokens

# def format_error(json_text: str, position: tuple[int, int], expected: list[TokenType], got: str) -> str:
#     lines: list[str] = json_text.splitlines()
#     line, column = position
#     error_line: str = lines[line - 1] if line - 1 < len(lines) else ""
#     caret_position: int = column - 1
#     caret_indicator: str = " " * caret_position + "^"
#     expected_tokens: str = "', '".join(t.name for t in expected)

#     return f"""Error: Parse error on line {line}:
# {error_line}
# {caret_indicator}
# Expecting '{expected_tokens}', got '{got}'"""
