#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import inspect
import time
from abc import ABC, abstractmethod
from logging import getLogger
from pathlib import Path
from typing import Any, Literal, Optional

import requests
import uri_template
from pydantic import BaseModel

from s2gos.client.config import ClientConfig
from s2gos.client.defaults import DEFAULT_SERVER_URL
from s2gos.client.exceptions import ClientException


logger = getLogger("s2gos")


class Transport(ABC):
    """Abstraction of the transport that calls the S2GOS web API."""

    @property
    @abstractmethod
    def config(self) -> ClientConfig:
        """The configuration."""

    @abstractmethod
    def call(
        self,
        path: str,
        method: Literal["get", "post", "put", "delete"],
        path_params: dict[str, Any],
        query_params: dict[str, Any],
        request: BaseModel | None,
        return_types: dict[str, type | None],
        error_types: dict[str, type | None],
    ) -> Any:
        """
        Call the S2GOS web API with the given endpoint
        `path`, `method`, `params`, etc. Then validate the response
        and return an instance of one of the types given by
        `return_types`.
        """


class DefaultTransport(Transport):
    """The concrete S2GOS web API transport."""

    def __init__(
        self,
        config_path: Optional[str | Path] = None,
        user_name: Optional[str] = None,
        access_token: Optional[str] = None,
        server_url: Optional[str] = None,
        debug: bool = False,
    ):
        default_config = ClientConfig.read(config_path=config_path)

        self._config = ClientConfig(
            user_name=user_name or default_config.user_name,
            access_token=access_token or default_config.access_token,
            server_url=server_url or default_config.server_url or DEFAULT_SERVER_URL,
        )

        self.debug = debug

    @property
    def config(self) -> ClientConfig:
        return self._config

    def call(
        self,
        path,
        method: Literal["get", "post", "put", "delete"],
        path_params: dict[str, Any],
        query_params: dict[str, Any],
        request: BaseModel | None,
        return_types: dict[str, type | None],
        error_types: dict[str, type | None],
    ) -> Any:
        url = f"{self.config.server_url}{uri_template.expand(path, **path_params)}"

        t0 = time.time()
        try:
            return _call(
                url,
                method,
                query_params,
                request,
                return_types,
                error_types,
            )
        finally:
            if self.debug:
                logger.debug(
                    "Calling service API took "
                    f"{round(1000 * (time.time() - t0))} milliseconds:\n"
                    "  url: %s\n"
                    "  path: %s\n"
                    "  method: %s\n"
                    "  path_params: %s\n"
                    "  query_params: %s\n"
                    "  request: %s\n"
                    "  return_types: %s\n",
                    # "  error_types: %s",
                    url,
                    path,
                    method,
                    path_params,
                    query_params,
                    request,
                    return_types,
                    # error_types,
                )


def _call(
    url: str,
    method: Literal["get", "post", "put", "delete"],
    query_params: dict[str, Any],
    request: BaseModel | None,
    return_types: dict[str, type | None],
    _error_types: dict[str, type | None],
) -> Any:
    data = (
        request.model_dump(
            mode="json", by_alias=True, exclude_none=True, exclude_defaults=True
        )
        if isinstance(request, BaseModel)
        else request
    )

    response = requests.request(
        method.upper(),
        url,
        params=query_params,
        json=data,
    )

    response_value = response.json()

    if response.ok:
        status_key = str(response.status_code)
        return_type = return_types.get(status_key)
        if (
            return_type is not None
            and inspect.isclass(return_type)
            and issubclass(return_type, BaseModel)
        ):
            return return_type.model_validate(response_value)
        else:
            return response_value
    else:
        kwargs = {}
        if isinstance(response_value, dict):
            kwargs = dict(
                title=response_value.get("title"),
                detail=response_value.get("detail"),
            )
        raise ClientException(response.status_code, response.reason, **kwargs)
