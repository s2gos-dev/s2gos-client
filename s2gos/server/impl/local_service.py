#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from s2gos.common.models import (
    Results,
    StatusInfo,
    Execute,
    JobList,
    Process,
    ProcessList,
    ProcessSummary,
    ConfClasses,
    LandingPage,
)
from s2gos.server.service import Service


class LocalService(Service):
    async def get_landing_page(self) -> LandingPage:
        return LandingPage(
            title="S2GOS API Server (local)",
            description="Local server implementing the OGC API - Processes 1.0 Standard",
            links=[],
        )

    async def get_conformance_classes(self) -> ConfClasses:
        return ConfClasses(conformsTo=["x", "y", "z"])

    async def get_processes(self) -> ProcessList:
        return ProcessList(
            processes=[
                ProcessSummary(
                    id="wf001",
                    version="0.1",
                    title="Workflow 1",
                    description="Test workflow #1",
                ),
                ProcessSummary(
                    id="wf002",
                    version="0.1",
                    title="Workflow 2",
                    description="Test workflow #2",
                ),
            ],
            links=[],
        )

    async def get_process_description(self, process_id: str) -> Process:
        raise NotImplementedError

    async def get_jobs(self) -> JobList:
        raise NotImplementedError

    async def execute(self, process_id: str, request: Execute) -> StatusInfo:
        raise NotImplementedError

    async def get_status(self, job_id: str) -> StatusInfo:
        raise NotImplementedError

    async def dismiss(self, job_id: str) -> StatusInfo:
        raise NotImplementedError

    async def get_result(self, job_id: str) -> Results:
        raise NotImplementedError
