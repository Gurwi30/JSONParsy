from tokenizer import TokenType


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