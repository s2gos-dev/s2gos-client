#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from typing import Any, Callable, TypeAlias, Optional

import pandas as pd
import panel as pn
import param
from IPython.display import display

from s2gos.common.models import JobList, StatusCode, StatusInfo

SelectedJobsAction: TypeAlias = Callable[[list[str]], Any]


class JobsTable(pn.viewable.Viewer):
    _jobs = param.List(default=[], doc="List of current jobs")

    def __init__(
        self,
        job_list: JobList,
        on_delete_jobs: Optional[SelectedJobsAction] = None,
        on_cancel_jobs: Optional[SelectedJobsAction] = None,
        on_restart_jobs: Optional[SelectedJobsAction] = None,
        on_get_job_results: Optional[SelectedJobsAction] = None,
    ):
        super().__init__()
        self._on_delete_jobs = on_delete_jobs
        self._on_cancel_jobs = on_cancel_jobs
        self._on_restart_jobs = on_restart_jobs
        self._on_get_job_results = on_get_job_results
        self._tabulator = self._new_tabulator(job_list)
        self._tabulator.param.watch(self._update_buttons, "selection")
        # A placeholder for clicked action
        self._cancel_button = pn.widgets.Button(
            name="Cancel",
            # tooltip="Cancels the selected job(s)",
            button_type="primary",
            on_click=self.cancel_selected_jobs,
            disabled=True,
        )
        self._delete_button = pn.widgets.Button(
            name="Delete",
            # tooltip="Deletes the selected job(s)",
            button_type="danger",
            on_click=self.delete_selected_jobs,
            disabled=True,
        )
        self._restart_button = pn.widgets.Button(
            name="Restart",
            # tooltip="Restarts the selected job(s)",
            button_type="primary",
            on_click=self.restart_selected_jobs,
            disabled=True,
        )
        self._results_button = pn.widgets.Button(
            name="Get Result",
            # tooltip="Gets the results from the selected job(s)",
            button_type="primary",
            on_click=self.get_selected_job_results,
            disabled=True,
        )
        self._action_row = pn.Row(
            self._cancel_button,
            self._delete_button,
            self._restart_button,
            self._results_button,
        )
        self._selected_text = pn.widgets.StaticText(name="Selection:", value="None")
        self._view = pn.Column(
            self._action_row,
            self._tabulator,
            self._selected_text,
        )

        # Reaction to changes in jobs list
        self.param.watch(self._on_jobs_changed, "_jobs")
        self._jobs = job_list.jobs

    def set_job_list(self, job_list: JobList):
        self._jobs = job_list.jobs

    def _on_jobs_changed(self, _event: Any = None):
        """Will be called automatically, if self.jobs changes."""
        df = self._jobs_to_dataframe(self._jobs)
        self._tabulator.value = df

    def _update_buttons(self, _event: Any = None):
        """Will be called if selection changes."""

        selected_jobs = self.selected_jobs
        self._selected_text.value = ", ".join([j.jobID for j in selected_jobs])

        self._cancel_button.disabled = self._on_cancel_jobs is None or self.is_disabled(
            selected_jobs, {StatusCode.accepted, StatusCode.running}
        )
        self._delete_button.disabled = self._on_delete_jobs is None or self.is_disabled(
            selected_jobs,
            {StatusCode.successful, StatusCode.dismissed, StatusCode.failed},
        )
        self._restart_button.disabled = (
            self._on_restart_jobs is None
            or self.is_disabled(
                selected_jobs,
                {StatusCode.successful, StatusCode.dismissed, StatusCode.failed},
            )
        )
        self._results_button.disabled = (
            self._on_get_job_results is None
            or self.is_disabled(
                selected_jobs, {StatusCode.successful, StatusCode.failed}
            )
        )

    @classmethod
    def is_disabled(cls, jobs: list[StatusInfo], requirements: set[StatusCode]):
        return not jobs or not all(j.status in requirements for j in jobs)

    @property
    def selected_jobs(self) -> list[StatusInfo]:
        """Get selected jobs from jobs table."""
        selection = self._tabulator.selection
        if not selection:
            return []
        selected_ids = {self._jobs[row].jobID for row in selection}
        return [job for job in self._jobs if job.jobID in selected_ids]

    def cancel_selected_jobs(self, event: Any):
        self._on_cancel_jobs([j.jobID for j in self.selected_jobs])

    def delete_selected_jobs(self, event: Any):
        self._on_delete_jobs([j.jobID for j in self.selected_jobs])

    def restart_selected_jobs(self, event: Any):
        self._on_restart_jobs([j.jobID for j in self.selected_jobs])

    def get_selected_job_results(self, event: Any):
        for r in self._on_get_job_results([j.jobID for j in self.selected_jobs]):
            display(r)

    def __panel__(self) -> pn.viewable.Viewable:
        return self._view

    @classmethod
    def _new_tabulator(cls, job_list: JobList) -> pn.widgets.Tabulator:
        dataframe = cls._jobs_to_dataframe(job_list.jobs)

        tabulator = pn.widgets.Tabulator(
            dataframe,
            theme="default",
            width=600,
            height=300,
            layout="fit_data",
            show_index=False,
            editors={},  # No editing
            # selectable=False,
            disabled=True,
            configuration={
                "columns": [
                    {"title": "Process ID", "field": "process_id"},
                    {"title": "Job ID", "field": "job_id"},
                    {"title": "Status", "field": "status"},
                    {
                        "title": "Progress",
                        "field": "progress",
                        "formatter": "progress",
                        "formatterParams": {
                            "min": 0,
                            "max": 100,
                            "color": [
                                "#f00",
                                "#ffa500",
                                "#ff0",
                                "#0f0",
                            ],  # red → orange → yellow → green
                        },
                    },
                    {"title": "Message", "field": "message"},
                    {
                        "title": "  ",
                        "field": "action",
                        "hozAlign": "center",
                        "formatter": "plaintext",
                        "cellClick": True,  # Needed to enable cell-level events
                        "cssClass": "action-cell",  # We'll style this column
                    },
                ]
            },
        )

        return tabulator

    @classmethod
    def _jobs_to_dataframe(cls, jobs: list[StatusInfo]):
        return pd.DataFrame([cls._job_to_dataframe_row(job) for job in jobs])

    @classmethod
    def _job_to_dataframe_row(cls, job: StatusInfo):
        return {
            "process_id": job.processID,
            "job_id": job.jobID,
            "status": job.status.value,
            "progress": job.progress or 0,
            "message": job.message or "-",
        }
