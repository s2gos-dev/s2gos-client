#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.


import inspect

from pydantic import BaseModel

from . import models

__all__ = []


def _patch_models():
    for name, obj in inspect.getmembers(models, inspect.isclass):
        if (
            not name.startswith("_")
            and obj.__module__ == models.__name__
            and issubclass(obj, BaseModel)
        ):
            # Make model object render nicely in Jupyter notebooks
            setattr(obj, "_repr_json_", _repr_base_model_as_json)


def _repr_base_model_as_json(self: BaseModel):
    return self.model_dump(mode="json", by_alias=True, exclude_none=True), dict(
        root=self.__class__.__name__ + " object:"
    )


_patch_models()
