from typing import Any
from tokenizer import Token, TokenType, TokenizationError, tokenize
from parser import ParsingError, parse_object, parse_array, parse_simple_value

def parse(json: str) -> Any:
    tokens: list[Token] = tokenize(json)

    try:
        match tokens[0].type:
            case TokenType.BEGIN_OBJECT:
                _, parsed = parse_object(tokens)
                return parsed

            case TokenType.BEGIN_ARRAY:
                _, parsed = parse_array(tokens)
                return parsed

            case _:
                return parse_simple_value(tokens[0])
    except ParsingError | TokenizationError as e:
        print(e.__class__.__name__)
        raise ParsingError(format_error(json, e.position, e.expected, e.got), e.position, e.expected, e.got)

def serialize(obj: dict) -> str:
    pass

def save(obj: dict, path: str) -> None:
    pass

def format_error(json_text: str, position: tuple[int, int], expected: list[TokenType], got: str) -> str:
    lines: list[str] = json_text.splitlines()
    line, column = position
    error_line: str = lines[line - 1] if line - 1 < len(lines) else ""
    caret_position: int = column - 1
    caret_indicator: str = " " * caret_position + "^"
    expected_tokens: str = "', '".join(t.name for t in expected)

    return f"""Error: Parse error on line {line}:
{error_line}
{caret_indicator}
Expecting '{expected_tokens}', got '{got}'"""