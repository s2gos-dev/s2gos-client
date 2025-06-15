#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures.process import ProcessPoolExecutor
from typing import Callable, Optional

from fastapi.responses import JSONResponse

from s2gos.common.models import (
    ConfClasses,
    Execute,
    JobList,
    LandingPage,
    Process,
    ProcessList,
    ProcessSummary,
    Results,
    StatusCode,
    StatusInfo,
)
from s2gos.server.exceptions import JSONContentException
from s2gos.server.service import Service

from .job import Job
from .process_registry import ProcessRegistry


class LocalService(Service):
    def __init__(
        self,
        title: str,
        description: Optional[str] = None,
        executor: Optional[ThreadPoolExecutor | ProcessPoolExecutor] = None,
    ):
        self.landing_page = LandingPage(title=title, description=description, links=[])
        self.executor = executor or ThreadPoolExecutor(max_workers=3)
        self.process_registry = ProcessRegistry()
        self.jobs: dict[str, Job] = {}

    async def get_landing_page(self) -> LandingPage:
        return self.landing_page

    async def get_conformance_classes(self) -> ConfClasses:
        return ConfClasses(
            conformsTo=[
                "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/core",
                "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/"
                "ogc-process-description",
                "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/json",
                # "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/html",
                "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/oas30",
                "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/job-list",
                # "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/callback",
                "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/dismiss",
            ]
        )

    async def get_processes(self) -> ProcessList:
        return ProcessList(
            processes=[
                ProcessSummary(
                    **p.model_dump(mode="python", exclude={"inputs", "outputs"})
                )
                for p in self.process_registry.get_process_list()
            ],
            links=[],
        )

    async def get_process_description(self, process_id: str) -> Process:
        process_entry = self.process_registry.get_entry(process_id)
        if process_entry is None:
            raise JSONContentException(404, detail=f"Process {process_id!r} not found")
        return process_entry.process

    async def execute(self, process_id: str, request: Execute) -> JSONResponse:
        process_entry = self.process_registry.get_entry(process_id)
        if process_entry is None:
            raise JSONContentException(404, detail=f"Process {process_id!r} not found")

        process_info = process_entry.process

        input_params = (
            request.model_dump(mode="json", include={"inputs"}).get("inputs") or {}
        )
        input_default_params = {
            input_name: input_info.schema_.default
            for input_name, input_info in process_info.inputs.items()
            if input_info.schema_.default is not None
        }
        function_kwargs = {}
        for input_name in process_info.inputs.keys():
            if input_name in input_params:
                function_kwargs[input_name] = input_params[input_name]
            elif input_name in input_default_params:
                function_kwargs[input_name] = input_default_params[input_name]

        print("input_params:", input_params)
        print("input_default_params:", input_default_params)
        print("params:", function_kwargs)

        job_id = f"job_{len(self.jobs)}"
        job = Job(
            process_id=process_info.id,
            job_id=job_id,
            function=process_entry.function,
            function_kwargs=function_kwargs,
        )
        self.jobs[job_id] = job
        job.future = self.executor.submit(job.run)
        # 201 means, async execution started
        return JSONResponse(
            status_code=201, content=job.status_info.model_dump(mode="json")
        )

    async def get_jobs(self) -> JobList:
        return JobList(jobs=[job.status_info for job in self.jobs.values()], links=[])

    async def get_status(self, job_id: str) -> StatusInfo:
        job = self._get_job(job_id, messages={})
        return job.status_info

    async def dismiss(self, job_id: str) -> StatusInfo:
        job = self._get_job(job_id, messages={})
        job.cancel()
        return job.status_info

    async def delete(self, job_id: str) -> None:
        self._get_job(
            job_id,
            messages={
                StatusCode.accepted: "is already accepted",
                StatusCode.running: "is still running",
            },
        )
        del self.jobs[job_id]

    async def get_result(self, job_id: str) -> Results:
        job = self._get_job(
            job_id,
            messages={
                StatusCode.accepted: "has not started yet",
                StatusCode.running: "is still running",
                StatusCode.dismissed: "has been cancelled",
                StatusCode.failed: "has failed",
            },
        )
        result = job.future.result()
        entry = self.process_registry.get_entry(job.status_info.processID)
        outputs = entry.process.outputs or {}
        output_count = len(outputs)
        return Results.model_validate(
            {
                output_name: result if output_count == 1 else result[i]
                for i, output_name in enumerate(outputs.keys())
            }
        )

    # TODO: be user-friendly, turn kwargs into parameter list
    def process_info(self, **kwargs) -> Callable[[Callable], Callable]:
        """A decorator for user functions to be registered as processes."""

        def _factory(function: Callable):
            self.register_process(function, **kwargs)
            return function

        return _factory

    def register_process(self, function: Callable, **kwargs) -> ProcessRegistry.Entry:
        """Register a user function as process."""
        return self.process_registry.register_function(function, **kwargs)

    def _get_job(self, job_id: str, messages: dict[StatusCode, str]) -> Job:
        job = self.jobs.get(job_id)
        if job is None:
            raise JSONContentException(404, detail=f"Job {job_id!r} does not exist")
        detail = messages.get(job.status_info.status)
        if detail:
            raise JSONContentException(403, detail=f"Job {job_id!r} {detail}")
        return job
