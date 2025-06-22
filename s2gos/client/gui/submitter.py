#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.
import datetime
from typing import Any, Callable, TypeAlias

import panel as pn
import param

from s2gos.client import ClientException
from s2gos.client.gui.js2panel import param_schema_to_widget
from s2gos.common.models import (
    Format,
    JobInfo,
    Output,
    Process,
    ProcessList,
    ProcessRequest,
    TransmissionMode,
)

SubmitRequestAction: TypeAlias = Callable[[str, ProcessRequest], JobInfo]
GetProcessAction: TypeAlias = Callable[[str], Process]


class Submitter(pn.viewable.Viewer):
    _processes = param.List(default=[], doc="List of process summaries")
    _process_descriptions = param.Dict(default={}, doc="Dictionary of cached processes")

    def __init__(
        self,
        process_list: ProcessList,
        process_list_error: ClientException | None,
        on_submit_request: SubmitRequestAction,
        on_get_process_description: GetProcessAction,
    ):
        super().__init__()
        self._processes = process_list.processes
        self._process_list_error = process_list_error

        self._on_submit_request = on_submit_request
        self._on_get_process_description = on_get_process_description

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
        self._process_select.param.watch(
            lambda e: self._on_process_id_changed(e.new), "value"
        )

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

        self._inputs_panel = pn.Column()
        self._outputs_panel = pn.Column()

        self._view = pn.Column(
            process_panel,
            self._inputs_panel,
            self._outputs_panel,
            action_panel,
        )

        self._input_widgets = {}
        self._output_widgets = {}

        self._on_process_id_changed(process_id)

    def __panel__(self) -> pn.viewable.Viewable:
        return self._view

    def _on_process_id_changed(self, process_id: str | None = None):
        process_description: Process | None = None
        process_markdown: str | None = None
        if not process_id:
            process_markdown = "_No process selected._"
        else:
            if process_id in self._process_descriptions:
                process_description = self._process_descriptions[process_id]
            else:
                try:
                    process_description = self._on_get_process_description(process_id)
                    self._process_descriptions[process_id] = process_description
                except ClientException as e:
                    process_description = None
                    process_markdown = (
                        f"**Error**: {e.title} (status `{e.status_code}`): {e.detail}"
                    )
            if process_description:
                process_markdown = (
                    f"**{process_description.title}**\n\n"
                    f"{process_description.description}"
                )

        self._process_doc_markdown.object = process_markdown
        if not process_description:
            self._submit_button.disabled = True
            self._input_widgets = {}
            self._output_widgets = {}
        else:
            self._submit_button.disabled = False
            self._input_widgets = {
                param_name: param_schema_to_widget(
                    param_name,
                    input_description.schema_.model_dump(
                        mode="json", exclude_defaults=True
                    ),
                    False,
                )
                for param_name, input_description in (
                    process_description.inputs or {}
                ).items()
            }
            self._output_widgets = {}

        self._inputs_panel[:] = self._input_widgets.values()
        self._outputs_panel[:] = self._output_widgets.values()

    def _on_submit_request_button_clicked(self, _event: Any = None):
        process_id = self._process_select.value
        process_description = self._process_descriptions.get(process_id)
        if process_description is None:
            return
        request = ProcessRequest(
            inputs={
                k: _serialize_for_json(v.value) for k, v in self._input_widgets.items()
            },
            outputs={
                k: Output(
                    format=Format(
                        mediaType="application/json",
                        encoding="UTF-8",
                        schema=process_description.outputs[k].schema_,
                    ),
                    transmissionMode=TransmissionMode.value,
                )
                for k, v in self._output_widgets.items()
            },
        )
        try:
            self._submit_button.disabled = True
            _status_info = self._on_submit_request(process_id, request)
            # TODO: Show status info in GUI
        except ClientException as e:
            # TODO: Show error in GUI
            print(f"error: {e}")
        finally:
            self._submit_button.disabled = False

    def _on_open_request_clicked(self, _event: Any = None):
        # TODO implement open request
        pass

    def _on_save_request_clicked(self, _event: Any = None):
        # TODO implement save request
        pass

    def _on_save_as_request_clicked(self, _event: Any = None):
        # TODO implement save request as
        pass

    def _update_buttons(self):
        # TODO implement action enablement
        pass


def _serialize_for_json(value: Any):
    # check if there are more cases to be handled
    if isinstance(value, datetime.date):
        return value.isoformat()
    return value
