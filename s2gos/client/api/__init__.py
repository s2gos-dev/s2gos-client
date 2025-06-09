#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import inspect

from pydantic import BaseModel

import s2gos.common.models as models

from .client import Client

__all__ = ["Client"]


def _add_members(module, predicate):
    for name, obj in inspect.getmembers(module, predicate):
        if not name.startswith("_") and obj.__module__ == module.__name__:
            # Make model object render nicely in Jupyter notebooks
            if issubclass(obj, BaseModel):
                if _repr_base_model_as_json is not None:
                    setattr(obj, "_repr_json_", _repr_base_model_as_json)

            globals()[name] = obj
            __all__.append(name)


def _repr_base_model_as_json(self: BaseModel):
    return self.model_dump(mode="json"), dict(root=self.__class__.__name__ + " object:")


_add_members(models, inspect.isclass)
