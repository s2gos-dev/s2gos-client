#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from typing import Callable, Optional
import inspect

from .registry import ProcessRegistry


def process(
    _registry: Optional[ProcessRegistry] = None, **kwargs
) -> Callable[[Callable], Callable]:
    def _factory(function: Callable):
        if not inspect.isfunction(function):
            raise ValueError(
                "The decorator '@process(...)' can only be applied to functions"
            )
        registry = (
            _registry
            if isinstance(_registry, ProcessRegistry)
            else ProcessRegistry.default
        )
        registry.register_function(function, **kwargs)
        return function

    return _factory
