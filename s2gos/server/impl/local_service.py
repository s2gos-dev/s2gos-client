#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from s2gos.common.models import (
    ConfClasses,
    LandingPage,
    Execute,
    InputDescription,
    JobList,
    MaxOccurs,
    OutputDescription,
    Process,
    ProcessList,
    ProcessSummary,
    Results,
    Schema,
    Schema1,
    StatusInfo,
)
from s2gos.server.exceptions import JSONContentException
from s2gos.server.service import Service

_landing_page = LandingPage(
    title="S2GOS API Server (local)",
    description="Local server implementing the OGC API - Processes 1.0 Standard",
    links=[],
)


# noinspection PyArgumentList
_processes_db = [
    Process(
        id="wf001",
        version="0.1",
        title="Workflow 1",
        description="Test workflow #1",
        inputs={
            "input": InputDescription(
                title="Input product",
                minOccurs=1,
                maxOccurs=1,
                schema=Schema(root=Schema1(type="string")),
            )
        },
        outputs={
            "output": OutputDescription(
                title="Output product",
                schema=Schema(root=Schema1(type="string")),
            )
        },
    ),
    Process(
        id="wf002",
        version="0.1",
        title="Workflow 2",
        description="Test workflow #2",
        inputs={
            "input": InputDescription(
                title="Input product",
                minOccurs=1,
                maxOccurs=MaxOccurs.unbounded,
                schema=Schema(root=Schema1(type="string")),
            )
        },
        outputs={
            "output": OutputDescription(
                title="Output product",
                schema=Schema(root=Schema1(type="string")),
            )
        },
    ),
]

_processes = [
    ProcessSummary(**p.model_dump(exclude={"inputs", "outputs"})) for p in _processes_db
]
_processes_dict = {p.id: p for p in _processes_db}


_conf_classes = ConfClasses(
    conformsTo=[
        "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/core",
        "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/ogc-process-description",
        "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/json",
        # Check: "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/html",
        "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/oas30",
        "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/job-list",
        # Not yet: "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/callback",
        "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/dismiss",
    ]
)


class LocalService(Service):
    async def get_landing_page(self) -> LandingPage:
        return _landing_page

    async def get_conformance_classes(self) -> ConfClasses:
        return _conf_classes

    async def get_processes(self) -> ProcessList:
        return ProcessList(
            processes=_processes,
            links=[],
        )

    async def get_process_description(self, process_id: str) -> Process:
        if process_id not in _processes_dict:
            raise JSONContentException(404, detail=f"Process {process_id!r} not found")
        return _processes_dict[process_id]

    async def get_jobs(self) -> JobList:
        # TODO: implement get_jobs()
        return JobList(jobs=[], links=[])

    async def get_status(self, job_id: str) -> StatusInfo:
        # TODO: implement get_status()
        raise JSONContentException(404, detail=f"Job {job_id!r} not found")

    async def execute(self, process_id: str, request: Execute) -> StatusInfo:
        if process_id not in _processes_dict:
            raise JSONContentException(404, detail=f"Process {process_id!r} not found")
        # TODO: implement execute()
        raise JSONContentException(501, detail="Not implemented")

    async def dismiss(self, job_id: str) -> StatusInfo:
        # TODO: implement dismiss()
        raise JSONContentException(404, detail=f"Job {job_id!r} not found")

    async def get_result(self, job_id: str) -> Results:
        # TODO: implement get_result()
        raise JSONContentException(404, detail=f"Job {job_id!r} not found")
