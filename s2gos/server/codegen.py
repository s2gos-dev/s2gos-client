from pathlib import Path
from typing import Any, IO

import yaml


_UNDEF = object()

_TYPES = {
    "null": "None",
    "boolean": "bool",
    "integer": "int",
    "number": "float",
    "string": "str",
    "array": "list[Any]",
    "object": "dict[str, Any]",
}

REF_PREFIX = "#/components/schemas/"


def to_py_literal(value) -> str:
    if isinstance(value, str):
        return f'"{value}"'
    return repr(value)


def to_py_union_type(py_types: list[str]) -> str:
    if any(t.startswith('"') for t in py_types):
        return f"Union[{', '.join(py_types)}]"
    else:
        return " | ".join(py_types)


def to_py_type(schema: dict[str, Any], path: str, optional: bool = False) -> str:
    ref_uri: str | None = schema.get("$ref")
    if ref_uri:
        assert ref_uri.startswith(REF_PREFIX)
        component_name = ref_uri[len(REF_PREFIX) :]
        type_name = component_name[0].upper() + component_name[1:]
        return '"' + type_name + '"'

    one_of: list[dict] | None = schema.get("oneOf")
    if one_of:
        return to_py_union_type(
            [to_py_type(s, path + f".oneOf[{i}]") for i, s in enumerate(one_of)]
        )

    any_of: list[dict] | None = schema.get("anyOf")
    if any_of:
        return to_py_union_type(
            [to_py_type(s, path + f".anyOf[{i}]") for i, s in enumerate(any_of)]
        )

    all_of: list[dict] | None = schema.get("allOf")
    if all_of:
        for i, s in enumerate(all_of):
            if s.get("$ref"):
                return to_py_type(s, path + f".allOf[{i}]")
        for i, s in enumerate(all_of):
            if s.get("type"):
                return to_py_type(s, path + f".allOf[{i}]")
        print(f"warn: cannot convert {path}.allOf")

    enum_ = schema.get("enum")
    if enum_:
        return f"Literal[{', '.join(to_py_literal(v) for v in enum_)}]"

    const = schema.get("const", _UNDEF)
    if const is not _UNDEF:
        return f"Literal[{to_py_literal(const)}]"

    json_type = schema.get("type")
    if json_type == "array":
        items_schema = schema.get("items")
        item_type = to_py_type(items_schema, path + ".type")
        py_type = f"list[{item_type}]"
    elif isinstance(json_type, str):
        py_type = _TYPES[json_type]
    elif isinstance(json_type, (list, tuple)):
        py_type = to_py_union_type([_TYPES[t] for t in json_type])
    else:
        print(f"warn: cannot convert {path}")
        py_type = "Any"
    return to_py_union_type([py_type, "None"]) if optional else py_type


def write_components(openapi_schema: dict[str, Any], stream: IO):
    component_schemas = openapi_schema["components"]["schemas"]
    stream.write("from typing import Any, Literal, TypeAlias, Union\n")
    stream.write("from dataclasses import dataclass\n")
    for component_name, component_schema in component_schemas.items():
        component_type = component_schema.get("type")
        py_component_name = component_name[0].upper() + component_name[1:]

        if component_type == "object":
            properties = component_schema.get("properties")
            additional_properties = component_schema.get("additionalProperties")
            required = component_schema.get("required", [])

            if properties:
                # assert additional_properties is None or additional_properties is False
                lines = [
                    "",
                    "@dataclass",
                    f"class {py_component_name}:",
                ]
                required_properties = [
                    convert_property(
                        component_name, property_name, property_schema, False
                    )
                    for property_name, property_schema in properties.items()
                    if property_name in required
                ]
                optional_properties = [
                    convert_property(
                        component_name, property_name, property_schema, True
                    )
                    for property_name, property_schema in properties.items()
                    if property_name not in required
                ]
                lines.extend(["    " + p for p in required_properties])
                lines.extend(["    " + p for p in optional_properties])
                lines.append("")
                stream.write("\n".join(lines))
            elif additional_properties:
                assert properties is None
                py_type = to_py_type(
                    additional_properties, component_name + ".additionalProperties"
                )
                stream.write(f"\n{py_component_name}: TypeAlias = {py_type}\n")
            else:
                stream.write(f"\n{py_component_name}: TypeAlias = dict[str, Any]\n")

        else:
            py_type = to_py_type(component_schema, component_name + ".type")
            stream.write(f"\n{py_component_name}: TypeAlias = {py_type}\n")


def convert_property(
    component_name: str,
    property_name: str,
    property_schema: dict[str, Any],
    optional: bool,
):
    py_type = to_py_type(
        property_schema,
        component_name + ".properties." + property_name,
        optional=optional,
    )
    py_property_name = (
        property_name[1:] if property_name.startswith("$") else property_name
    )

    default = _UNDEF
    if optional:
        default = property_schema.get("default", _UNDEF)
        if default is _UNDEF:
            const = schema.get("const", _UNDEF)
            if const is not _UNDEF:
                default = const
        if default is _UNDEF:
            default = None

    property_def = f"{py_property_name}: {py_type}"
    if default is not _UNDEF:
        property_def += f" = {to_py_literal(default)}"

    return property_def


def get_openapi_schema():
    schema_path = Path(__file__).parent / "openapi.yaml"
    with schema_path.open() as stream:
        return yaml.load(stream, Loader=yaml.SafeLoader)


if __name__ == "__main__":
    schema = get_openapi_schema()
    with Path("_components.py").open("wt") as f:
        write_components(schema, f)
