import threading
import time
from typing import Callable, Optional

import pandas as pd
import panel as pn

from s2gos.common.models import JobList, StatusInfo


class JobsTable:
    def __init__(self, job_list_provider: Callable[[], JobList], interval: float = 2.0):
        self._job_list_provider = job_list_provider
        self._update_interval = interval  # seconds
        self._update_thread: Optional[threading.Thread] = None
        self._tabulator: Optional[pn.widgets.Tabulator] = None

    def show_jobs(self):
        if (
            self._tabulator is not None
            and self._update_thread is not None
            and self._update_thread.is_alive()
        ):
            return self._tabulator

        self._tabulator = pn.widgets.Tabulator(
            self._to_dataframe(),
            theme="default",
            width=600,
            height=300,
            layout="fit_data",
            show_index=False,
            editors={},  # No editing
            formatters={
                "Progress (%)": {
                    "type": "progress",
                    "min": 0,
                    "max": 100,
                    "color": ["#f00", "#ffa500", "#0f0"],  # red → orange → green
                },
            },
            disabled=True,
        )

        self._update_thread = threading.Thread(target=self._run_updater, daemon=True)
        self._update_thread.start()

        return self._tabulator

    def cancel(self):
        self._update_thread = None

    def _run_updater(self):
        while self._update_thread:
            time.sleep(self._update_interval)
            self._tabulator.value = self._to_dataframe()

    def _to_dataframe(self):
        job_list = self._job_list_provider()
        jobs: list[StatusInfo] = job_list.jobs
        return pd.DataFrame(
            [
                {
                    "Job ID": job.jobID,
                    "Status": str(job.status),
                    "Progress (%)": job.progress or 0,
                    "Message": job.message or "-",
                }
                for job in jobs
            ]
        )
