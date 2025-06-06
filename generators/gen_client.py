#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import subprocess
from pathlib import Path
from typing import Literal

import datetime

from generators.common import (
    C_TAB,
    D_TAB,
    OPEN_API_PATH,
    S2GOS_PATH,
    camel_to_snake,
    to_py_type,
    parse_responses,
    write_file,
)
from generators.openapi import load_openapi_schema, OASchema, OAMethod

GENERATOR_NAME = str(Path(__file__).name)

CLIENT_PATH = S2GOS_PATH / "client" / "api" / "client.py"


def main():
    schema = load_openapi_schema(OPEN_API_PATH)
    models: set[str] = set()
    code = generate_api_code(schema, models)
    model_list = ", ".join(sorted(models))

    write_file(
        GENERATOR_NAME,
        CLIENT_PATH,
        [
            "from typing import Optional\n",
            "\n",
            f"from s2gos.common.models import {model_list}\n",
            "from .service import DefaultService, Service",
            "\n",
            "class Client:\n",
            f'{C_TAB}"""\n',
            f"{C_TAB}The S2GOS Client API.\n",
            "\n",
            f"{C_TAB}Args:\n",
            f"{C_TAB}{D_TAB}service: Optional API service instance.\n",
            f"{C_TAB}{D_TAB}kwargs: "
            "Configuration passed to `DefaultService` constructor.\n",
            f"{C_TAB}{D_TAB}{D_TAB}if `service` is not provided.\n",
            f'{C_TAB}"""\n',
            "\n",
            f"{C_TAB}def __init__(self, *, "
            f"service: Optional[Service] = None, **kwargs):\n",
            f"{C_TAB}{C_TAB}self._service = "
            "DefaultService(**kwargs) if service is None else service\n",
            "\n",
            code,
        ],
    )


def generate_api_code(schema: OASchema, models: set[str]) -> str:
    functions: list[str] = []
    for path, endpoint in schema.paths.items():
        for method_name, method in endpoint.items():
            # noinspection PyTypeChecker
            function_code = generate_function_code(path, method_name, method, models)
            functions.append(function_code)
    return "\n\n".join(functions)


def generate_function_code(
    path: str,
    method_name: Literal["get", "post", "put", "delete"],
    method: OAMethod,
    models: set[str],
) -> str:
    param_args: list[str] = ["self"]
    param_kwargs: list[str] = []
    path_param_mappings: list[str] = []
    query_param_mappings: list[str] = []
    for parameter in method.parameters:
        param_name = camel_to_snake(parameter.name)
        param_type = "Any"
        param_default: str | None = None
        if parameter.schema_:
            param_type = to_py_type(
                parameter.schema_,
                f"{method.operationId}.{parameter.name}",
                models,
            )
            default_value = parameter.schema_.get("default", ...)
            if default_value is not ...:
                param_default = repr(default_value)
        if param_default is None:
            param_args.append(f"{param_name}: {param_type}")
        else:
            param_kwargs.append(f"{param_name}: {param_type} = {param_default}")
        if parameter.in_ == "path":
            path_param_mappings.append(f"{parameter.name!r}: {param_name}")
        elif parameter.in_ == "query":
            query_param_mappings.append(f"{parameter.name!r}: {param_name}")
        else:
            print(
                f"⚠️ Error: parameter {parameter.name!r}"
                f" in {parameter.in_!r} not supported"
            )

    request_type: str | None = None
    if method.requestBody:
        request_type = "Any"
        json_content = method.requestBody.content.get("application/json")
        if json_content and json_content.schema_:
            request_type = to_py_type(
                json_content.schema_, f"{method.operationId}.requestBody", models
            )
        if method.requestBody.required:
            param_args.append(f"request: {request_type}")
        else:
            param_kwargs.append(f"request: Optional[{request_type}] = None")

    param_list = ", ".join([*param_args, *param_kwargs])
    path_param_dict = "{" + ", ".join(path_param_mappings) + "}"
    query_param_dict = "{" + ", ".join(query_param_mappings) + "}"

    return_types, error_types = parse_responses(method, models)

    if not return_types:
        return_types = {"200": "None"}

    function_doc = generate_function_doc(method)
    return_type_union = " | ".join(set(v[0] for v in return_types.values()))
    return_type_dict = (
        "{" + ", ".join([f"{k!r}: {v[0]}" for k, v in return_types.items()]) + "}"
    )
    error_type_dict = (
        "{" + ", ".join([f"{k!r}: {v[0]}" for k, v in error_types.items()]) + "}"
    )
    return (
        f"{C_TAB}def {camel_to_snake(method.operationId)}({param_list})"
        f" -> {return_type_union}:\n"
        f"{function_doc}"
        f"{C_TAB}{C_TAB}return self._service.call("
        f"path={path!r}, "
        f"method={method_name!r}, "
        f"path_params={path_param_dict}, "
        f"query_params={query_param_dict}, "
        f"request={'request' if request_type else 'None'}, "
        f"return_types={return_type_dict}, "
        f"error_types={error_type_dict}"
        f")\n"
    )


def generate_function_doc(method: OAMethod) -> str:
    doc_lines = method.description.split("\n") if method.description else []

    if method.parameters:
        if doc_lines and doc_lines[-1] != "":
            doc_lines.append("")
        doc_lines.append("Params:")
        for parameter in method.parameters:
            param_name = camel_to_snake(parameter.name)
            if parameter.description:
                param_desc_lines = parameter.description.split("\n")
                doc_lines.append(f"{D_TAB}{param_name}: {param_desc_lines[0]}")
                doc_lines.extend(
                    [f"{2 * D_TAB}{line}" for line in param_desc_lines[1:]]
                )
            else:
                doc_lines.append(f"{D_TAB}{param_name}:")

    # TODO: split long lines that exceed 80 characters

    if method.requestBody:
        json_content = method.requestBody.content.get("application/json")
        if json_content:
            if method.requestBody.description:
                param_desc_lines = method.requestBody.description.split("\n")
                doc_lines.append(f"{D_TAB}request: {param_desc_lines[0]}")
                doc_lines.extend(
                    [f"{D_TAB}{D_TAB}{line}" for line in param_desc_lines[1:]]
                )
            else:
                doc_lines.append("  request:")

    return_types, error_types = parse_responses(method, set())

    def append_responses(
        resp_title: str, resp_types: dict[str, tuple[str, list[str]]], lines: list[str]
    ):
        lines.append("")
        lines.append(f"{resp_title}:")
        for resp_code, (resp_type, desc_lines) in resp_types.items():
            if desc_lines:
                lines.append(f"{D_TAB}{resp_type}: {desc_lines[0]}")
                for desc_line in desc_lines[1:]:
                    lines.append(f"{D_TAB}{D_TAB}{desc_line}")
            else:
                lines.append(f"{D_TAB}{resp_type}:")

    if return_types:
        append_responses("Returns", return_types, doc_lines)

    if error_types:
        append_responses("Raises", error_types, doc_lines)

    doc_lines = [
        '"""',
        *doc_lines,
        '"""',
    ]
    doc_lines = [f"{2 * C_TAB}{line}" for line in doc_lines]
    return "\n".join(doc_lines) + "\n"


if __name__ == "__main__":
    main()
