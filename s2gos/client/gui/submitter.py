#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from typing import Any, Callable, TypeAlias

import panel as pn
import param

from s2gos.client.gui.js2panel import param_schema_to_widget
from s2gos.common.models import Execute, Process, ProcessList

SubmitRequestAction: TypeAlias = Callable[[str, Execute], Any]
GetProcessAction: TypeAlias = Callable[[str], Process]


class Submitter(pn.viewable.Viewer):
    _processes = param.List(default=[], doc="List of process summaries")
    _process_descriptions = param.Dict(default={}, doc="Dictionary of cached processes")
    _execute = param.Parameter(
        default=Execute(), doc="Currently edited processing request"
    )

    def __init__(
        self,
        process_list: ProcessList,
        on_submit_request: SubmitRequestAction,
        on_get_process_description: GetProcessAction,
    ):
        super().__init__()
        self.on_submit_request = on_submit_request
        self.on_get_process_description = on_get_process_description

        process_select_options = [p.id for p in process_list.processes]
        if process_select_options:
            process_id = process_select_options[0]
        else:
            process_id = process_select_options

        self._process_select = pn.widgets.Select(
            name="Process",
            options=process_select_options,
            value=process_select_options[0] if process_select_options else None,
        )
        self._process_select.param.watch(lambda e: self._update_process(e.new), "value")

        self._process_doc_markdown = pn.pane.Markdown("")
        process_panel = pn.Column(
            # pn.pane.Markdown("# Process"),
            self._process_select,
            self._process_doc_markdown,
        )

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

        self._input_params_panel = pn.Column()
        self._output_params_panel = pn.Column()

        inputs_panel = pn.Column(
            pn.pane.Markdown("## Inputs"), self._input_params_panel
        )
        outputs_panel = pn.Column(
            pn.pane.Markdown("## Outputs"), self._output_params_panel
        )

        self._view = pn.Column(
            process_panel,
            inputs_panel,
            outputs_panel,
            action_panel,
        )

        self._processes = process_list.processes
        self._update_process(process_id)

    def _update_process(self, process_id: str | None = None):
        if not process_id:
            self._process_doc_markdown.object = "_No process selected._"
            self._input_params_panel[:] = []
            self._output_params_panel[:] = []
            return

        if process_id in self._process_descriptions:
            process_description = self._process_descriptions[process_id]
        else:
            process_description = self.on_get_process_description(process_id)
            self._process_descriptions[process_id] = process_description

        # print(process_description)
        self._process_doc_markdown.object = (
            f"**{process_description.title}**\n\n{process_description.description}"
        )

        input_widgets = [
            param_schema_to_widget(
                param_name,
                input_description.schema_.model_dump(
                    mode="json", exclude_defaults=True
                ),
                False,
            )
            for param_name, input_description in (
                process_description.inputs or {}
            ).items()
        ]

        output_widgets = [
            param_schema_to_widget(
                param_name,
                output_description.schema_.model_dump(
                    mode="json", exclude_defaults=True
                ),
                False,
            )
            for param_name, output_description in (
                process_description.outputs or {}
            ).items()
        ]

        self._input_params_panel[:] = input_widgets
        self._output_params_panel[:] = output_widgets

    def _on_submit_request_button_clicked(self, _event: Any = None):
        pass

    def _on_open_request_clicked(self, _event: Any = None):
        pass

    def _on_save_request_clicked(self, _event: Any = None):
        pass

    def _on_save_as_request_clicked(self, _event: Any = None):
        pass

    def _update_buttons(self):
        pass

    def __panel__(self) -> pn.viewable.Viewable:
        return self._view
