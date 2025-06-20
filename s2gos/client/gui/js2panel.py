#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from typing import Any

import panel as pn
import param

from .bboxselect import BoundingBoxSelector

TYPES = "boolean", "integer", "number", "string", "array"
DEFAULTS = {"boolean": False, "integer": 0, "number": 0.0, "string": "", "array": []}


def params_schema_to_widgets(schema: dict[str, Any]) -> dict[str, param.Parameterized]:
    widgets = {}
    for param_name, param_schema in schema["properties"].items():
        required = param_name in schema.get("required", [])
        widget = param_schema_to_widget(param_name, param_schema, required)
        if widget is not None:
            widgets[param_name] = widget
    return widgets


def param_schema_to_widget(
    param_name: str, param_schema: dict[str, Any], _required: bool
) -> param.Parameterized | None:
    if "type" not in param_schema:
        raise ValueError("missing 'type' property")
    type_ = param_schema["type"]
    if not isinstance(type_, str) or type_ not in TYPES:
        raise ValueError(
            f"value of 'type' property must be one of {TYPES}, was {type_!r}"
        )

    title = param_schema.get("title", param_name.replace("_", " ").capitalize())
    value = param_schema.get("default", DEFAULTS.get(type_))

    if type_ == "boolean":
        return pn.widgets.Checkbox(name=title, value=value)

    if type_ == "integer":
        return pn.widgets.IntSlider(
            name=title,
            start=param_schema.get("minimum", 0),
            end=param_schema.get("maximum", 100),
            value=value,
            step=1,
        )
    if type_ == "number":
        return pn.widgets.FloatSlider(
            name=title,
            start=param_schema.get("minimum", 0),
            end=param_schema.get("maximum", 100),
            value=value,
            step=1,
        )

    if type_ == "string":
        if "enum" in param_schema:
            return pn.widgets.Select(
                name=title, options=param_schema["enum"], value=value
            )
        elif param_schema.get("format") == "date":
            value = value or None
            return pn.widgets.DatePicker(name=title, value=value)
        else:
            return pn.widgets.TextInput(name=title, value=value)

    if type_ == "array":
        if param_schema.get("format") == "bbox":
            return BoundingBoxSelector(name=title)

    return None
