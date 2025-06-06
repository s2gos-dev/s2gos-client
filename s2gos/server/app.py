#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .exceptions import JSONContentException

app = FastAPI()


@app.exception_handler(JSONContentException)
async def json_http_exception_handler(
    _request: Request, exc: JSONContentException
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.content.model_dump(),
    )
