
from typing import Any
from src.utils.error_utils import LexerError
from src.lexer.tokenizer import Token, TokenType


class ParsingError(LexerError):
    
    def __init__(self, message: str, position: tuple[int, int], expected: list[TokenType], got: str):
        super().__init__(message, position, [token.value for token in expected], got)


def parse_object(tokens: list[Token], start_idx: int = 0) -> tuple[int, Any]:
    if tokens[start_idx].type != TokenType.BEGIN_OBJECT:
        raise create_expected_error([TokenType.BEGIN_OBJECT], tokens[start_idx], "Invalid object syntax!")

    parsed_object: dict[str, Any] = {}
    i: int = start_idx + 1

    while i < len(tokens):
        token: Token = tokens[i]

        if token.type == TokenType.END_OBJECT:
            return i - start_idx, parsed_object

        if token.type != TokenType.STRING:
            raise create_expected_error([TokenType.STRING], token, "Object keys must be strings!")

        key = token.value

        if tokens[i + 1].type != TokenType.NAME_SEPARATOR:
            raise create_expected_error([TokenType.NAME_SEPARATOR], tokens[i + 1])

        value_token: Token = tokens[i + 2]

        match value_token.type:
            case TokenType.NUMBER | TokenType.STRING | TokenType.NULL | TokenType.TRUE | TokenType.FALSE:
                value = parse_simple_value(value_token)
                parsed_object[key] = value
                offset = 0

            case TokenType.BEGIN_ARRAY:
                offset, sub_array = parse_array(tokens, i + 2)
                parsed_object[key] = sub_array

            case TokenType.BEGIN_OBJECT:
                offset, sub_object = parse_object(tokens, i + 2)
                parsed_object[key] = sub_object

            case _:
                raise create_expected_error(
                    [TokenType.NUMBER, TokenType.STRING, TokenType.NULL, TokenType.TRUE, TokenType.FALSE, TokenType.BEGIN_ARRAY, TokenType.BEGIN_OBJECT],
                    value_token,
                    "Invalid value type!"
                )

        i += 3 + offset

        if i >= len(tokens):
            break

        token = tokens[i]

        if token.type == TokenType.VALUE_SEPARATOR:
            i += 1
            if tokens[i].type == TokenType.END_OBJECT:
                raise create_expected_error([TokenType.END_OBJECT], token)
        elif token.type != TokenType.END_OBJECT:
            raise create_expected_error([TokenType.END_OBJECT, TokenType.VALUE_SEPARATOR], token)

    raise create_expected_error([TokenType.END_OBJECT], token)

def parse_array(tokens: list[Token], start_idx: int = 0) -> tuple[int, list[Any]]:
    if tokens[start_idx].type != TokenType.BEGIN_ARRAY:
        raise create_expected_error([TokenType.BEGIN_ARRAY], tokens[start_idx], "Invalid array syntax!")

    parsed_array: list[Any] = []
    i: int = start_idx + 1

    while i < len(tokens):
        token: Token = tokens[i]

        if i > start_idx and tokens[i - 1].type == TokenType.VALUE_SEPARATOR:
            if token.type in {TokenType.VALUE_SEPARATOR, TokenType.NAME_SEPARATOR, TokenType.END_ARRAY}:
                raise create_expected_error(
                    [TokenType.NUMBER, TokenType.STRING, TokenType.NULL, TokenType.TRUE, TokenType.FALSE, TokenType.BEGIN_ARRAY, TokenType.BEGIN_OBJECT],
                    token,
                    "Invalid array syntax! Unexpected token after ','"
                )
            
        if token.type == TokenType.END_ARRAY:
            return i - start_idx, parsed_array

        match token.type:
            case TokenType.NUMBER | TokenType.STRING | TokenType.NULL | TokenType.TRUE | TokenType.FALSE:
                value = parse_simple_value(token)
                parsed_array.append(value)

            case TokenType.BEGIN_ARRAY:
                offset, sub_array = parse_array(tokens, i)
                parsed_array.append(sub_array)
                i += offset

            case TokenType.BEGIN_OBJECT:
                offset, sub_object = parse_object(tokens, i)
                parsed_array.append(sub_object)
                i += offset

        i += 1

    raise create_expected_error([TokenType.END_ARRAY], token)

def parse_simple_value(token: Token) -> Any:
    match token.type:
        case TokenType.NUMBER:
            return int(token.value) if token.value.isdigit() else float(token.value)

        case TokenType.STRING:
            return token.value

        case TokenType.NULL:
            return None

        case TokenType.TRUE:
            return True

        case TokenType.FALSE:
            return False

        case _:
            raise create_expected_error(
                [TokenType.NUMBER, TokenType.STRING, TokenType.NULL, TokenType.TRUE, TokenType.FALSE],
                token,
                "Unable to parse simple value"
            )

def create_expected_error(expected: list[TokenType], token: Token, msg: str = "") -> ParsingError:
    return ParsingError(
        f"{msg + ' ' or ''}Expecting '{', '.join(t.value for t in expected)}', got '{token.type.value}'",
        token.position,
        expected,
        token.value
    )