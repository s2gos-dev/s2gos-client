#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import s2gos.common.models as models
from .client import Client
import inspect

__all__ = ["Client"]


def _add_members(module, predicate):
    for name, obj in inspect.getmembers(module, predicate):
        if not name.startswith("_") and obj.__module__ == module.__name__:
            globals()[name] = obj
            __all__.append(name)


_add_members(models, inspect.isclass)
