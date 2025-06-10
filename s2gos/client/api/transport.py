#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import inspect
from abc import ABC, abstractmethod
from logging import getLogger
from pathlib import Path
from typing import Any, Literal, Optional

import requests
import uri_template
from pydantic import BaseModel

from s2gos.client.config import Config
from s2gos.client.defaults import DEFAULT_SERVER_URL


class Transport(ABC):
    """Abstraction of the transport that calls the S2GOS web API."""

    @property
    @abstractmethod
    def config(self) -> Config:
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
        default_config = Config.read(config_path=config_path)

        self._config = Config(
            user_name=user_name or default_config.user_name,
            access_token=access_token or default_config.access_token,
            server_url=server_url or default_config.server_url or DEFAULT_SERVER_URL,
        )

        self.debug = debug

    @property
    def config(self) -> Config:
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

        if self.debug:
            logger = getLogger("s2gos")
            logger.debug(
                "Calling service API:\n"
                "  url: %s\n"
                "  path: %s\n"
                "  method: %s\n"
                "  path_params: %s\n"
                "  query_params: %s\n"
                "  request: %s\n"
                "  return_types: %s\n"
                "  error_types: %s",
                url,
                path,
                method,
                path_params,
                query_params,
                request,
                return_types,
                error_types,
            )

        data = (
            request.model_dump(mode="json", by_alias=True, exclude_none=True)
            if isinstance(request, BaseModel)
            else request
        )

        response = requests.request(
            method.upper(),
            url,
            params=query_params,
            json=data,
        )
        if response.ok:
            status_key = str(response.status_code)
            return_type = return_types.get(status_key)
            if return_type is None:
                return_type = return_types.get("200")
            if (
                return_type is not None
                and inspect.isclass(return_type)
                and issubclass(return_type, BaseModel)
            ):
                return return_type.model_validate(response.json())
            return response.json()
        else:
            # TODO: raise dedicated ClientException
            raise ValueError(response.json())
