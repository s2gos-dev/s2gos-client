#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from unittest import TestCase

from panel.layout import Panel

from s2gos.client.gui.processes_form import ProcessesForm
from s2gos.common.models import (
    InputDescription,
    JobInfo,
    ProcessDescription,
    ProcessList,
    ProcessRequest,
    Schema,
    StatusCode,
    Type,
)

bbox_input = InputDescription(
    title="Bounding box",
    schema=Schema.model_validate(
        {
            "type": "array",
            "items": {"type": "number"},
            "format": "bbox",
        }
    ),
)

date_input = InputDescription(
    title="Date",
    schema=Schema.model_validate(
        {
            "type": "string",
            "format": "date",
            "default": "2025-01-01",
        }
    ),
)

int_input = InputDescription(
    title="Periodicity",
    schema=Schema.model_validate(
        {
            "type": "integer",
            "minimum": 1,
            "maximum": 10,
        },
    ),
)


class SubmitterTest(TestCase):
    def test_submitter_with_int_input(self):
        submitter = _create_submitter({"periodicity": int_input})
        self.assertIsInstance(submitter.__panel__(), Panel)

    def test_submitter_bbox_input(self):
        submitter = _create_submitter({"bbox": bbox_input})
        self.assertIsInstance(submitter.__panel__(), Panel)

    def test_submitter_with_date_input(self):
        submitter = _create_submitter({"date": date_input})
        self.assertIsInstance(submitter.__panel__(), Panel)


def _create_submitter(process_inputs: dict[str, InputDescription]) -> ProcessesForm:
    process = ProcessDescription(
        id="gen_scene",
        title="Generate a scene",
        version="1",
        inputs=process_inputs,
    )

    def on_get_process(process_id: str):
        return process

    def on_execute_process(process_id: str, _request: ProcessRequest):
        return JobInfo(
            processID=process_id,
            jobID="job_8",
            type=Type.process,
            status=StatusCode.successful,
        )

    process_list = ProcessList(processes=[process], links=[])

    return ProcessesForm(
        process_list,
        None,
        on_get_process=on_get_process,
        on_execute_process=on_execute_process,
    )
