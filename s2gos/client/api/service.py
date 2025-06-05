#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from abc import abstractmethod, ABC
from logging import getLogger
from typing import Any, Literal

from pydantic import BaseModel


class Service(ABC):
    """Abstraction of the S2GOS web API service."""

    @abstractmethod
    def call(
        self,
        path: str,
        method: Literal["get", "post", "put", "delete"],
        params: dict[str, Any],
        request: BaseModel | None,
        return_types: dict[str, type | None],
        error_types: dict[str, type | None],
    ) -> Any:
        """
        Call the S2GOS API service with the given endpoint
        `path`, `method`, `params`. Then validate the response
        and return an instance of one of the types given by
        `return_types`.
        """


class DefaultService(Service):
    """The concrete S2GOS web API service."""

    def __init__(self, debug: bool = False, **kwargs):
        # TODO: expand, document and use kwargs
        self.debug = debug

    def call(
        self,
        path,
        method: Literal["get", "post", "put", "delete"],
        params: dict[str, Any],
        request: BaseModel | None,
        return_types: dict[str, type | None],
        error_types: dict[str, type | None],
    ) -> Any:
        # TODO: implement DefaultService.call()

        if self.debug:
            logger = getLogger("s2gos")
            logger.debug(
                "Calling service API:\n"
                "  path: %s\n"
                "  method: %s\n"
                "  params: %s\n"
                "  request: %s\n"
                "  return_types: %s\n"
                "  error_types: %s",
                path,
                method,
                params,
                request,
                return_types,
                error_types,
            )

        return_type = return_types["200"]
        return return_type() if return_type is not None else None
