#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import threading
import time
from typing import Optional

from s2gos.client import Client as GeneratedClient
from s2gos.client import ClientException
from s2gos.client.gui.jobstable import JobsTable
from s2gos.client.gui.submitter import Submitter
from s2gos.client.transport import Transport
from s2gos.common.models import JobInfo, JobList, ProcessList, ProcessRequest


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
        self._submitter: Optional[Submitter] = None
        self._jobs_table: Optional[JobsTable] = None

    def show_submitter(self):
        if self._submitter is None:
            self._submitter = Submitter(
                *self._get_processes(),
                on_get_process_description=self._get_process_description,
                on_submit_request=self._submit_request,
            )
        return self._submitter

    def _get_process_description(self, process_id: str):
        return self.get_process_description(process_id)

    def _submit_request(self, process_id: str, request: ProcessRequest) -> JobInfo:
        return self.execute(process_id, request)

    def show_jobs(self):
        if self._jobs_table is None:
            self._jobs_table = JobsTable(
                *self._get_jobs(),
                on_cancel_job=self._cancel_job,
                on_delete_job=self._delete_job,
                on_restart_job=self._restart_job,
                on_get_job_result=self._get_job_result,
            )

        if self._update_thread is None or not self._update_thread.is_alive():
            self._update_thread = threading.Thread(
                target=self._run_updater, daemon=True
            )
            self._update_thread.start()

        return self._jobs_table

    def stop_updating(self):
        self._update_thread = None

    def _cancel_job(self, job_id: str):
        return self.dismiss(job_id)

    def _delete_job(self, job_id: str):
        return self.dismiss(job_id)

    # noinspection PyMethodMayBeStatic
    def _restart_job(self, _job_id: str):
        # TODO: implement job restart
        print("Not implemented.")

    # noinspection PyMethodMayBeStatic
    def _get_job_result(self, job_id: str):
        return self.get_result(job_id)

    def __delete__(self, instance):
        self._update_thread = None
        self._jobs_table = None

    def _run_updater(self):
        while self._update_thread is not None:
            time.sleep(self._update_interval)
            if self._jobs_table is not None:
                self._jobs_table.set_job_list(*self._get_jobs())

    def _get_processes(self) -> tuple[ProcessList, ClientException | None]:
        try:
            return self.get_processes(), None
        except ClientException as e:
            return ProcessList(processes=[], links=[]), e

    def _get_jobs(self) -> tuple[JobList, ClientException | None]:
        try:
            return self.get_jobs(), None
        except ClientException as e:
            return JobList(jobs=[], links=[]), e
