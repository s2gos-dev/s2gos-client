#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import datetime
import time
from concurrent.futures import ThreadPoolExecutor

from fastapi.responses import JSONResponse

from s2gos.common.models import (
    ConfClasses,
    Execute,
    InputDescription,
    JobControlOptions,
    JobList,
    LandingPage,
    OutputDescription,
    Process,
    ProcessList,
    ProcessSummary,
    Results,
    Schema,
    StatusCode,
    StatusInfo,
    Type,
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
        id=f"process_{i}",
        version="1.0",
        title=f"Computes constant {result}",
        description=f"Computes {result}, which will take ~{duration} seconds",
        jobControlOptions=[JobControlOptions.async_execute, JobControlOptions.dismiss],
        inputs={
            "duration": InputDescription(
                title="Duration of the process",
                minOccurs=0,
                maxOccurs=1,
                schema=Schema.model_validate({"type": "number", "default": duration}),
            ),
            "fail": InputDescription(
                title="Whether to raise an error",
                minOccurs=0,
                maxOccurs=1,
                schema=Schema.model_validate({"type": "boolean", "default": False}),
            ),
        },
        outputs={
            "result": OutputDescription(
                title="Result of the computation",
                schema=Schema.model_validate({"type": "number"}),
            )
        },
    )
    for i, (duration, result) in enumerate([(3, 3.142), (10, 137.036), (60, 42.0)])
]

_process_summaries = [
    ProcessSummary(**p.model_dump(mode="python", exclude={"inputs", "outputs"}))
    for p in _processes_db
]

_processes_dict = {p.id: p for p in _processes_db}


_conf_classes = ConfClasses(
    conformsTo=[
        "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/core",
        "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/"
        "ogc-process-description",
        "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/json",
        # Check: "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/html",
        "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/oas30",
        "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/job-list",
        # Not yet: "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/callback",
        "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/dismiss",
    ]
)


class Job:
    def __init__(
        self,
        process_id: str,
        job_id: str,
        *,
        duration: float = 3.0,
        fail: bool = False,
    ):
        self.status_info = StatusInfo(
            type=Type.process,
            processID=process_id,
            jobID=job_id,
            status=StatusCode.accepted,
            created=datetime.datetime.now(),
        )
        self.duration = duration
        self.fail = fail
        self.cancelled = False

    def cancel(self):
        self.cancelled = True

    def check_cancellation(self) -> bool:
        if self.cancelled:
            self.status_info.status = StatusCode.dismissed
            return True
        return False

    def run(self):
        if self.check_cancellation():
            return
        self.status_info.status = StatusCode.running
        self.status_info.started = datetime.datetime.now()
        for i in range(101):
            if self.check_cancellation():
                return
            self.status_info.progress = i
            self.status_info.updated = datetime.datetime.now()
            if self.fail and i == 50:
                self.status_info.status = StatusCode.failed
                raise OSError("Write failed")
            time.sleep(self.duration / 100)
        if self.check_cancellation():
            return
        self.status_info.status = StatusCode.successful
        self.status_info.finished = datetime.datetime.now()


class LocalService(Service):
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.jobs: dict[str, Job] = {}

    async def get_landing_page(self) -> LandingPage:
        return _landing_page

    async def get_conformance_classes(self) -> ConfClasses:
        return _conf_classes

    async def get_processes(self) -> ProcessList:
        return ProcessList(
            processes=_process_summaries,
            links=[],
        )

    async def get_process_description(self, process_id: str) -> Process:
        if process_id not in _processes_dict:
            raise JSONContentException(404, detail=f"Process {process_id!r} not found")
        return _processes_dict[process_id]

    async def execute(self, process_id: str, request: Execute) -> JSONResponse:
        if process_id not in _processes_dict:
            raise JSONContentException(404, detail=f"Process {process_id!r} not found")

        inputs = request.model_dump(mode="json", include={"inputs"}).get("inputs") or {}

        job_id = f"job_{len(self.jobs)}"
        job = Job(
            process_id=process_id,
            job_id=job_id,
            **inputs,
        )
        self.jobs[job_id] = job
        self.executor.submit(job.run)
        # 201 means, async execution started
        return JSONResponse(
            status_code=201, content=job.status_info.model_dump(mode="json")
        )

    async def dismiss(self, job_id: str) -> StatusInfo:
        if job_id not in self.jobs:
            raise JSONContentException(404, detail=f"Job {job_id!r} not found")
        job = self.jobs[job_id]
        job.cancel()
        return job.status_info

    async def get_jobs(self) -> JobList:
        return JobList(jobs=[job.status_info for job in self.jobs.values()], links=[])

    async def get_status(self, job_id: str) -> StatusInfo:
        if job_id not in self.jobs:
            raise JSONContentException(404, detail=f"Job {job_id!r} not found")
        job = self.jobs[job_id]
        return job.status_info

    async def get_result(self, job_id: str) -> Results:
        if job_id not in self.jobs:
            raise JSONContentException(404, detail=f"Job {job_id!r} not found")

        job = self.jobs[job_id]
        if job.status_info.status != StatusCode.successful:
            detail = f"Job {job_id!r} is not ready"
            if job.status_info.status == StatusCode.accepted:
                detail = f"Job {job_id!r} has not started"
            elif job.status_info.status == StatusCode.running:
                detail = f"Job {job_id!r} is running"
            elif job.status_info.status == StatusCode.dismissed:
                detail = f"Job {job_id!r} is cancelled"
            elif job.status_info.status == StatusCode.failed:
                detail = f"Job {job_id!r} failed"
            raise JSONContentException(404, detail=detail)

        return Results.model_validate({"result": 42})
