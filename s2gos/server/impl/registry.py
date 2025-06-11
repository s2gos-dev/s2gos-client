#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.
import datetime
from typing import Callable, Optional, Any
import inspect
import dataclasses

from cffi.model import UnionType

from s2gos.common.models import Process, InputDescription, OutputDescription, Schema


@dataclasses.dataclass
class ProcessRegistryEntry:
    function: Callable
    signature: inspect.Signature
    process: Process


class ProcessRegistry:
    default: "ProcessRegistry"

    def __init__(self):
        self._dict: dict[str, ProcessRegistryEntry] = {}

    def get_process_list(self) -> list[Process]:
        return [v.process for k, v in self._dict.items()]

    def get_process(self, process_id: str) -> Optional[Process]:
        entry = self._dict.get(process_id)
        return entry.process if entry is not None else None

    def register_function(self, function: Callable, **kwargs) -> ProcessRegistryEntry:
        if not inspect.isfunction(function):
            raise ValueError("function argument must be callable")
        id_ = kwargs.pop("id", f"{function.__module__}:{function.__name__}")
        version = kwargs.pop("version", "0.0.0")
        inputs = kwargs.pop("inputs", {}) or {}
        outputs = kwargs.pop("outputs", {}) or {}
        signature = inspect.signature(function)

        if len(outputs):
            if signature.return_annotation:
                print(signature.return_annotation)
                pass

        if inputs:
            unknown_input_names = [
                k for k in inputs.keys() if k not in signature.parameters
            ]
            if unknown_input_names:
                raise ValueError(
                    f"Invalid input name(s): {', '.join(unknown_input_names)}"
                )
            for param_name, param in signature.parameters.items():
                if param_name not in inputs:
                    inputs[param_name] = _generate_input(param)
        else:
            inputs = {
                param_name: _generate_input(param)
                for param_name, param in signature.parameters.items()
            }

        if not outputs:
            outputs = _generate_outputs(signature.return_annotation)

        entry = ProcessRegistryEntry(
            function,
            signature,
            Process(id=id_, version=version, inputs=inputs, outputs=outputs, **kwargs),
        )
        self._dict[id_] = entry
        return entry


def _generate_input(param: inspect.Parameter) -> InputDescription:
    return InputDescription(schema=Schema.model_validate(_param_to_schema(param)))


def _generate_outputs(return_annotation) -> dict[str, OutputDescription]:
    return {}


def _param_to_schema(param: inspect.Parameter) -> dict[str, Any]:
    simple_types = {
        bool: {"type": "boolean"},
        int: {"type": "integer"},
        float: {"type": "number"},
        str: {"type": "string"},
        tuple: {"type": "array", "items": {}},
        list: {"type": "array", "items": {}},
        set: {"type": "array", "items": {}},
        dict: {"type": "object", "additionalProperties": {}},
        datetime.date: {"type": "boolean", "format": "date"},
        datetime.datetime: {"type": "boolean", "format": "datetime"},
    }
    schema = dict(simple_types.get(param.annotation, {}))
    if param.default is not inspect.Parameter.empty:
        schema["default"] = param.default
    return schema


ProcessRegistry.default = ProcessRegistry()
