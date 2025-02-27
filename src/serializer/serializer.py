from collections.abc import Iterable


class JSONEntity:

    def serialize(self, indent: int = 0) -> str:
        return serialize_object(self.__dict__, indent)


def serialize_object(data: dict[str, object], indent: int = 0) -> str:
    length: int = len(data)
    result: str = "{"

    for i, (key, value) in enumerate(data.items()):
        result += get_indent(indent) + f'"{key}": '
        simple_value: str = serialize_value(value)

        if not simple_value is None:
            result += simple_value
        elif isinstance(value, dict):
            result += serialize_object(value, indent + indent)[:-1] + (" " * indent) + "}"
        elif is_iterable(value):
            result += serialize_array(value, indent + indent)[:-1] + (" " * indent) + "]"
        elif isinstance(value, JSONEntity):
            result += f'{value.serialize(indent + indent)[:-1] + (" " * indent) + "}"}'
        else:
            raise ValueError(f"Unsupported data type: {type(value)}")

        if i < length - 1: 
            result += ", "
    
    return result + ("\n" if indent else "") + "}"

def serialize_array(data: list[object], indent: int = 0) -> str:
    length: int = len(data)
    result: str = "["

    for i, value in enumerate(data):
        result += get_indent(indent)
        simple_value: str = serialize_value(value)

        if not simple_value is None:
            result += simple_value
        elif isinstance(value, dict):
            result += serialize_object(value, indent + indent)[:-1] + (" " * indent) + "}"
        elif isinstance(value, list):
            result += serialize_array(value, indent + indent)[:-1] + (" " * indent) + "]"
        elif isinstance(value, JSONEntity):
            result += f'"{value.serialize(indent + indent)[:-1] + (" " * indent) + "}"}"'
        else:
            raise ValueError(f"Unsupported data type: {type(value)}")

        if i < length - 1: 
            result += ", "

    return result + ("\n" if indent else "") + "]"

def serialize_value(value: object) -> str | None:
    if value is None:
        return "null"
    elif isinstance(value, str):
        return f'"{value}"'
    elif isinstance(value, bool):
        return str(value).lower()
    elif isinstance(value, (int, float)):
        return str(value)
    else:
        return None

def get_indent(indent: int) -> str:
    return ("\n" if indent else "") + (" " * indent)

def is_iterable(obj):
    return isinstance(obj, Iterable) and not isinstance(obj, (str, dict))