#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import dataclasses
import inspect
from typing import (
    Any,
    Callable,
    Optional,
    get_args,
    get_origin,
)

from s2gos.common.models import InputDescription, OutputDescription, Process, Schema
from s2gos.server.services.local.schema_factory import Annotation, SchemaFactory


class ProcessRegistry:
    @dataclasses.dataclass
    class Entry:
        function: Callable
        signature: inspect.Signature
        process: Process

    def __init__(self):
        self._dict: dict[str, ProcessRegistry.Entry] = {}

    def get_process_list(self) -> list[Process]:
        return [v.process for v in self._dict.values()]

    def get_process(self, process_id: str) -> Optional[Process]:
        entry = self._dict.get(process_id)
        return entry.process if entry is not None else None

    def get_entry(self, process_id: str) -> Optional["ProcessRegistry.Entry"]:
        return self._dict.get(process_id)

    def register_function(
        self, function: Callable, **kwargs
    ) -> "ProcessRegistry.Entry":
        if not inspect.isfunction(function):
            raise ValueError("function argument must be callable")

        fn_name = f"{function.__module__}:{function.__qualname__}"

        id_ = kwargs.pop("id", fn_name)
        version = kwargs.pop("version", "0.0.0")
        inputs = kwargs.pop("inputs", None) or {}
        outputs = kwargs.pop("outputs", None) or {}
        description = kwargs.pop("description", function.__doc__)

        signature = inspect.signature(function)
        if not inputs:
            inputs = _generate_inputs(fn_name, signature)
        else:
            inputs = _complete_inputs(fn_name, signature, inputs)

        if not outputs:
            outputs = _generate_outputs(fn_name, signature.return_annotation)
        else:
            outputs = _complete_outputs(fn_name, signature, outputs)

        entry = ProcessRegistry.Entry(
            function,
            signature,
            Process(
                id=id_,
                version=version,
                description=description,
                inputs=inputs,
                outputs=outputs,
                **kwargs,
            ),
        )
        self._dict[id_] = entry
        return entry


def _generate_inputs(
    fn_name: str, signature: inspect.Signature
) -> dict[str, InputDescription]:
    return {
        param_name: _generate_input(fn_name, param)
        for param_name, param in signature.parameters.items()
        if param_name != "ctx"
    }


def _complete_inputs(
    fn_name: str, signature: inspect.Signature, inputs: dict[str, InputDescription]
):
    assert isinstance(inputs, dict)
    unknown_input_names = [k for k in inputs.keys() if k not in signature.parameters]
    if unknown_input_names:
        raise ValueError(f"Invalid input name(s): {', '.join(unknown_input_names)}")
    _inputs = dict(inputs)
    for param_name, param in signature.parameters.items():
        if param_name not in inputs:
            _inputs[param_name] = _generate_input(fn_name, param)
    return _inputs


def _generate_input(fn_name: str, parameter: inspect.Parameter) -> InputDescription:
    return InputDescription(schema=_schema_from_parameter(fn_name, parameter))


def _generate_outputs(
    fn_name: str, annotation: Annotation
) -> dict[str, OutputDescription]:
    origin = get_origin(annotation)
    args = get_args(annotation)
    if origin is tuple and args:
        return {
            f"result_{i}": _generate_output(fn_name, f"result_{i}", arg)
            for i, arg in enumerate(args)
        }
    else:
        return {"result": _generate_output(fn_name, "result", annotation)}


def _complete_outputs(
    _fn_name: str, _signature: inspect.Signature, outputs: dict[str, OutputDescription]
):
    assert isinstance(outputs, dict)
    # TODO: implement _complete_outputs()
    return dict(outputs)


def _generate_output(
    fn_name: str, name: str, annotation: Annotation
) -> OutputDescription:
    return OutputDescription(
        schema=_schema_from_return_annotation(fn_name, name, annotation)
    )


def _schema_from_parameter(fn_name: str, parameter: inspect.Parameter) -> Schema:
    return SchemaFactory(
        fn_name,
        parameter.name,
        _normalize_inspect_value(parameter.annotation, default=Any),
        default=_normalize_inspect_value(parameter.default, default=...),
    ).get_schema()


def _schema_from_return_annotation(
    fn_name: str,
    name: str,
    annotation: Annotation,
) -> Schema:
    return SchemaFactory(
        fn_name,
        name,
        _normalize_inspect_value(annotation, default=Any),
        is_return=True,
    ).get_schema()


def _normalize_inspect_value(value: Any, *, default: Any) -> Any:
    if value is inspect.Parameter.empty:
        return default
    return value
