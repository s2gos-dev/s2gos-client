#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from typing import Any, Callable, TypeAlias

import panel as pn
import param

from s2gos.common.models import ProcessSummary, Process

SubmitRequestAction: TypeAlias = Callable[[dict[str, Any]], Any]
GetProcessAction: TypeAlias = Callable[[str], Process]


class SubmitForm(pn.viewable.Viewer):
    _process_summaries = param.List(default=[], doc="List of process summaries")
    _processes = param.Dict(default=[], doc="Dictionary of cached processes")

    def __init__(
        self,
        process_summaries: list[ProcessSummary],
        on_submit_request: SubmitRequestAction,
        on_get_process: GetProcessAction,
    ):
        super().__init__()
        self.on_submit_request = on_submit_request
        self.on_get_process = on_get_process

        self._process_select = pn.widgets.Select(
            name="Process",
            options=[p.id for p in process_summaries],
            value=None,
        )
        process_panel = pn.Column(self._process_select)

        self._submit_button = pn.widgets.Button(
            name="Submit",
            # tooltip="Submits the current request",
            button_type="primary",
            on_click=self._on_submit_request_button_clicked,
            disabled=True,
        )
        self._open_button = pn.widgets.Button(
            name="Open",
            on_click=self._on_open_request_clicked,
            disabled=True,
        )
        self._save_button = pn.widgets.Button(
            name="Save",
            on_click=self._on_save_request_clicked,
            disabled=True,
        )
        self._save_as_button = pn.widgets.Button(
            name="Save As...",
            on_click=self._on_save_as_request_clicked,
            disabled=True,
        )

        action_panel = pn.Row(
            self._submit_button,
            self._open_button,
            self._save_button,
            self._save_as_button,
        )

        inputs_panel = pn.Column(pn.widgets.StaticText(name="Inputs"))
        outputs_panel = pn.Column(pn.widgets.StaticText(name="Outputs"))

        self._view = pn.Column(
            process_panel,
            inputs_panel,
            outputs_panel,
            action_panel,
        )

        self._process_summaries = process_summaries
        self._processes = {}

    def _on_submit_request_button_clicked(self, _event: Any = None):
        pass

    def _on_open_request_clicked(self, _event: Any = None):
        pass

    def _on_save_request_clicked(self, _event: Any = None):
        pass

    def _on_save_as_request_clicked(self, _event: Any = None):
        pass

    def _update_buttons(self):
        """Will be called if selection changes."""

    def __panel__(self) -> pn.viewable.Viewable:
        return self._view
