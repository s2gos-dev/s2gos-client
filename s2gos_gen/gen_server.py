#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.


from pathlib import Path
from typing import Literal

from s2gos_gen.common import (
    C_TAB,
    OPEN_API_PATH,
    S2GOS_PATH,
    camel_to_snake,
    to_py_type,
    parse_responses,
    write_file,
)
from s2gos_gen.openapi import load_openapi_schema, OASchema, OAMethod


GENERATOR_NAME = str(Path(__file__).name)

ROUTES_PATH = S2GOS_PATH / "server" / "routes.py"
SERVICE_PATH = S2GOS_PATH / "server" / "service.py"


def main():
    schema = load_openapi_schema(OPEN_API_PATH)
    models: set[str] = set()
    routes_code, service_code = generate_code_for_paths(schema, models)
    model_list = ", ".join(sorted(models))

    write_file(
        GENERATOR_NAME,
        ROUTES_PATH,
        [
            f"from s2gos.common.models import {model_list}\n",
            "from .app import app\n",
            "from .provider import ServiceProvider\n",
            "\n",
            routes_code,
        ],
    )

    write_file(
        GENERATOR_NAME,
        SERVICE_PATH,
        [
            "from abc import ABC, abstractmethod\n",
            "\n",
            f"from s2gos.common.models import {model_list}\n",
            "\n",
            "class Service(ABC):\n",
            service_code,
        ],
    )


def generate_code_for_paths(schema: OASchema, models: set[str]) -> tuple[str, str]:
    route_functions: list[str] = []
    service_methods: list[str] = []
    for path, endpoint in schema.paths.items():
        for method_name, method in endpoint.items():
            # noinspection PyTypeChecker
            route_function, service_method = generate_method_code(
                path, method_name, method, models
            )
            route_functions.append(route_function)
            service_methods.append(service_method)
    return "\n\n".join(route_functions), "\n\n".join(service_methods)


def generate_method_code(
    path: str,
    method_name: Literal["get", "post", "put", "delete"],
    method: OAMethod,
    models: set[str],
) -> tuple[str, str]:
    pos_params: list[str] = []
    kw_params: list[str] = []
    pos_service_params: list[str] = []
    kw_service_params: list[str] = []
    service_args: list[str] = []
    service_kwargs: list[str] = []
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
            pos_params.append(f"{parameter.name}: {param_type}")
            pos_service_params.append(f"{param_name}: {param_type}")
            service_args.append(f"{param_name}={parameter.name}")
        else:
            kw_params.append(f"{parameter.name}: {param_type} = {param_default}")
            kw_service_params.append(f"{param_name}: {param_type}")
            service_kwargs.append(f"{param_name}={parameter.name}")

    if method.requestBody:
        request_type = "Any"
        json_content = method.requestBody.content.get("application/json")
        if json_content and json_content.schema_:
            request_type = to_py_type(
                json_content.schema_, f"{method.operationId}.requestBody", models
            )
        if method.requestBody.required:
            request_pos_param = f"request: {request_type}"
            pos_params.append(request_pos_param)
            pos_service_params.append(request_pos_param)
        else:
            request_kw_param = f"request: Optional[{request_type}] = None"
            kw_params.append(request_kw_param)
            kw_service_params.append(request_kw_param)
        service_args.append("request=request")

    param_list = ", ".join([*pos_params, *kw_params])
    service_param_list = ", ".join(["self", *pos_service_params, *kw_service_params])
    param_service_list = ", ".join([*service_args, *service_kwargs])

    return_types, error_types = parse_responses(method, models, skip_errors=True)

    if not return_types:
        return_types = {"200": "None"}

    return_type_union = " | ".join(set(v[0] for v in return_types.values()))
    py_op_name = camel_to_snake(method.operationId)
    return (
        (
            f"# noinspection PyPep8Naming\n"
            f"@app.{method_name}({path!r})\n"
            f"async def {py_op_name}({param_list})"
            f" -> {return_type_union}:\n"
            f"{C_TAB}return await ServiceProvider.instance().{py_op_name}({param_service_list})\n"
        ),
        (
            f"{C_TAB}@abstractmethod\n"
            f"{C_TAB}async def {py_op_name}({service_param_list})"
            f" -> {return_type_union}:\n"
            f"{C_TAB}{C_TAB}pass\n"
        ),
    )


if __name__ == "__main__":
    main()
