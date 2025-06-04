#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import datetime
from typing import Any

import panel as pn
from panel.layout import Panel

from .js2panel import params_schema_to_widgets


pn.extension("ipywidgets")


def create(params_schema: dict[str, Any]) -> Panel:
    """Create a UI from given parameter schema.

    Args:
        params_schema: A JSON object schema whose `properties`
            describe the allowed parameters.
    Return:
        A S2GOS GUI for the given `params_schema` of type
        `panel.layout.Panel`.
    """
    form_widgets = params_schema_to_widgets(params_schema)
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
        f"# {params_schema['title']}",
        form,
        submit_button,
        "## Submitted Parameters",
        output,
    )
