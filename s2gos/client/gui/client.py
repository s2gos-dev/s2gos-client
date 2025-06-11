#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import threading
import time
from typing import Optional

from s2gos.client import Client as GeneratedClient, ClientException
from s2gos.client.gui.jobstable import JobsTable
from s2gos.client.transport import Transport
from s2gos.common.models import JobList


class Client(GeneratedClient):
    def __init__(
        self,
        *,
        update_interval: float = 2.0,
        _transport: Optional[Transport] = None,
        **config,
    ):
        super().__init__(_transport=_transport, **config)
        self._update_interval = update_interval
        self._update_thread: Optional[threading.Thread] = None
        self._jobs_table: Optional[JobsTable] = None

    def show_jobs(self):
        if self._jobs_table is None:
            self._jobs_table = JobsTable(self._get_jobs())

        if self._update_thread is None or not self._update_thread.is_alive():
            self._update_thread = threading.Thread(
                target=self._run_updater, daemon=True
            )
            self._update_thread.start()

        return self._jobs_table

    def stop_updating(self):
        self._update_thread = None

    def __delete__(self, instance):
        self._update_thread = None
        self._jobs_table = None

    def _run_updater(self):
        while self._update_thread is not None:
            time.sleep(self._update_interval)
            if self._jobs_table is not None:
                self._jobs_table.set_job_list(self._get_jobs())

    def _get_jobs(self) -> JobList:
        try:
            job_list = self.get_jobs()
        except ClientException as e:
            job_list = JobList(jobs=[], links=[])
            # TODO: handle error in GUI
            print(f"Error: {e}")
        return job_list
