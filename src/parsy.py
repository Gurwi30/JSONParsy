from typing import Any
from src.utils.error_utils import LexerError
from src.lexer.tokenizer import Token, TokenType, TokenizationError, tokenize
from src.lexer.parser import ParsingError, parse_object, parse_array, parse_simple_value

class JSONSyntaxError(Exception):

    def __init__(self, message: str):
        super().__init__(message)

def parse(json: str) -> Any:
    try:
        tokens: list[Token] = tokenize(json)

        match tokens[0].type:
            case TokenType.BEGIN_OBJECT:
                _, parsed = parse_object(tokens)
                return parsed

            case TokenType.BEGIN_ARRAY:
                _, parsed = parse_array(tokens)
                return parsed

            case _:
                return parse_simple_value(tokens[0])
    except LexerError as e:
        raise JSONSyntaxError(format_error(json, e.position, e.expected, e.got))

def serialize(obj: dict) -> str:
    pass

def save(obj: dict, path: str) -> None:
    pass

def format_error(json_text: str, position: tuple[int, int], expected: list[str], got: str) -> str:
    lines: list[str] = json_text.splitlines()
    line, column = position
    error_line: str = lines[line - 1] if line - 1 < len(lines) else ""
    caret_position: int = column - 1
    caret_indicator: str = " " * caret_position + "^"
    expected_tokens: str = "', '".join(expected)

    return f"""Parse error on line {line}:
{error_line}
{caret_indicator}
Expecting '{expected_tokens}', got '{got}'"""