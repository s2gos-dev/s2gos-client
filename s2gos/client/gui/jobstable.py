#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import pandas as pd
import panel as pn
from panel.models.tabulator import CellClickEvent

from s2gos.common.models import JobList, StatusCode, StatusInfo

# Style the action column for hover effect
style = """
<style>
.tabulator .cell:hover {
    background-color: #f0f0f0;
    cursor: pointer;
    font-weight: bold;
}
.tabulator .delete-cell:hover {
    background-color: #f0f0f0;
    cursor: pointer;
    font-weight: bold;
}
</style>
"""

_action_to_icon = {
    "get_result": "⬇️",
    "dismiss": "✖️",
    "execute": "♻️️",  # restart
    "delete": "❌️",
}

_status_to_action = {
    StatusCode.successful.value: "get_result",
    StatusCode.accepted.value: "dismiss",
    StatusCode.running.value: "dismiss",
    StatusCode.failed.value: "execute",
    StatusCode.dismissed.value: "execute",
}


class JobsTable(pn.viewable.Viewer):
    def __init__(self, job_list: JobList, **params):
        super().__init__(**params)
        self._tabulator = self.new_tabulator(job_list)
        # A placeholder for clicked action
        self._clicked = pn.widgets.StaticText(name="Last action clicked:", value="None")

    def __panel__(self) -> pn.viewable.Viewable:
        return pn.Column(
            pn.pane.HTML(style),
            self._tabulator,
            self._clicked,
        )

    def set_job_list(self, job_list: JobList):
        self._tabulator.value = self._jobs_to_dataframe(job_list)

    def new_tabulator(self, job_list: JobList) -> pn.widgets.Tabulator:
        dataframe = self._jobs_to_dataframe(job_list)

        # Define the callback
        def on_click(event: CellClickEvent):
            if event.column == "action" or event.column == "delete":
                row_index = event.row
                job_data = dataframe.iloc[row_index]
                if event.column == "action":
                    action = _status_to_action.get(job_data.get("status", ""), "")
                else:
                    action = "delete"
                self._clicked.value = f"{action} {job_data['job_id']}"

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
                    {
                        "title": "  ",
                        "field": "delete",
                        "hozAlign": "center",
                        "formatter": "plaintext",
                        "cellClick": True,  # Needed to enable cell-level events
                        "cssClass": "action-cell",  # We'll style this column
                    },
                ]
            },
        )

        tabulator.on_click(on_click)

        return tabulator

    @classmethod
    def _job_to_dataframe_row(cls, job: StatusInfo):
        action = _status_to_action.get(job.status.value, "")
        action_icon = _action_to_icon.get(action, "")
        delete_icon = _action_to_icon.get("delete", "")
        return {
            "process_id": job.processID,
            "job_id": job.jobID,
            "status": job.status.value,
            "progress": job.progress or 0,
            "message": job.message or "-",
            "action": action_icon,
            "delete": delete_icon,
        }

    @classmethod
    def _jobs_to_dataframe(cls, job_list: JobList):
        jobs: list[StatusInfo] = job_list.jobs or []
        return pd.DataFrame([cls._job_to_dataframe_row(job) for job in jobs])
