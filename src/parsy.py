from typing import Any
from src.utils.error_utils import LexerError
from src.lexer.tokenizer import Token, TokenType, tokenize
from src.lexer.parser import parse_object, parse_array, parse_simple_value
from src.serializer.serializer import JSONEntity, serialize_object, serialize_array, is_iterable

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

def serialize(value: object) -> str:
    if value is None:
        return "null"
    elif isinstance(value, dict):
        return serialize_object(value)
    elif is_iterable(value):
        return serialize_array(value)
    elif isinstance(value, str):
        return f'"{value}"'
    elif isinstance(value, bool):
        return str(value).lower()
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, JSONEntity):
        return value.serialize()
    else:
        raise ValueError(f"Unsupported data type: {type(value)}")

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