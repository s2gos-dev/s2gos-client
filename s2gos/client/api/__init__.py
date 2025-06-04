#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import s2gos.common.models as client_models
from . import api as client_api
import inspect

__all__ = []


def _add_members(module, predicate):
    for name, obj in inspect.getmembers(module, predicate):
        if not name.startswith("_") and obj.__module__ == module.__name__:
            globals()[name] = obj
            __all__.append(name)


_add_members(client_api, inspect.isfunction)
_add_members(client_models, inspect.isclass)
