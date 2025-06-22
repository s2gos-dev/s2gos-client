#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import datetime
from typing import Any

import panel as pn
import param
from panel.layout import Panel

from s2gos.client.gui.js2panel import param_schema_to_widget

pn.extension("ipywidgets")


params_schema = {
    "title": "S2GOS Job Configuration",
    "type": "object",
    "properties": {
        "dataset": {
            "type": "string",
            "enum": ["Landsat-8", "Sentinel-2", "MODIS"],
            "title": "Dataset",
        },
        "region": {
            "type": "array",
            "title": "Region of Interest",
            "format": "bbox",
            "items": {"type": "number"},
            "minItems": 4,
            "maxItems": 4,
        },
        "start_date": {"type": "string", "format": "date", "title": "Start Date"},
        "end_date": {"type": "string", "format": "date", "title": "End Date"},
        "cloud_threshold": {
            "type": "number",
            "minimum": 0,
            "maximum": 100,
            "title": "Max Cloud Coverage (%)",
        },
        "include_ndvi": {"type": "boolean", "title": "Include NDVI in Output"},
    },
    "required": ["dataset", "region", "start_date", "end_date"],
}


def create_ui(schema: dict[str, Any]) -> Panel:
    """Create a UI from given parameter schema.

    Args:
        schema: A JSON object schema whose `properties`
            describe the allowed parameters.
    Return:
        A S2GOS GUI for the given `params_schema` of type
        `panel.layout.Panel`.
    """
    form_widgets = params_schema_to_widgets(schema)
    form = pn.Column(*form_widgets.values())
    output = pn.pane.JSON(height=200)

    def serialize_for_json(value):
        if isinstance(value, datetime.date):
            return value.isoformat()
        return value

    def on_submit(event=None):
        values = {
            key: serialize_for_json(widget.value)
            for key, widget in form_widgets.items()
        }
        output.object = values

    submit_button = pn.widgets.Button(name="Submit Job", button_type="primary")
    submit_button.on_click(on_submit)

    return pn.Column(
        f"# {schema['title']}",
        form,
        submit_button,
        "## Submitted Parameters",
        output,
    )


def params_schema_to_widgets(schema: dict[str, Any]) -> dict[str, param.Parameterized]:
    widgets = {}
    for param_name, param_schema in schema["properties"].items():
        required = param_name in schema.get("required", [])
        widget = param_schema_to_widget(param_name, param_schema, required)
        if widget is not None:
            widgets[param_name] = widget
    return widgets


ui = create_ui(params_schema)
ui.servable()
