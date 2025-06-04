#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from abc import abstractmethod, ABC
from typing import Any, Literal, Optional, TypeVar

T = TypeVar("T")


class Service(ABC):
    """Abstraction of the S2GOS web API service."""

    _default: Optional["Service"] = None

    @classmethod
    def default(cls) -> "Service":
        """Get the default service."""
        if cls._default is None:
            cls._default = DefaultService()
        return cls._default

    @classmethod
    def set_default(cls, service: "Service") -> Optional["Service"]:
        """Set the default service."""
        old_service = cls._default
        cls._default = service
        return old_service

    @abstractmethod
    def call(
        self,
        path: str,
        method: Literal["get", "post", "put", "delete"],
        params: dict[str, Any],
        request: Any,
        return_type: type[T],
    ) -> T:
        """
        Call the S2GOS API service with the given endpoint
        `path`, `method`, `params`. Then validate the response
        and return an instance of the type given by `return_type`.
        """


class DefaultService(Service):
    """The concrete S2GOS web API service."""

    def call(
        self,
        path,
        method: Literal["get", "post", "put", "delete"],
        params: dict[str, Any],
        request: Any,
        return_type: type[T],
    ) -> T:
        # TODO: implement DefaultService.call()
        print("Calling service API:")
        print("  path:", path)
        print("  method:", method)
        print("  params:", params)
        print("  return_type:", return_type)
        return return_type()
