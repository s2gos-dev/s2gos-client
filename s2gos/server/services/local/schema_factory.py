#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import copy
import datetime
from types import GenericAlias, NoneType, UnionType
from typing import Any, TypeAlias, Union, get_args, get_origin

from s2gos.common.models import Schema

Annotation: TypeAlias = type | GenericAlias | UnionType | NoneType


class SchemaFactory:
    unary_schemas: dict[type, dict[str, Any]] = {
        NoneType: {"nullable": True},
        bool: {"type": "boolean"},
        int: {"type": "integer"},
        float: {"type": "number"},
        str: {"type": "string"},
        tuple: {"type": "array"},
        list: {"type": "array"},
        set: {"type": "array"},
        dict: {"type": "object"},
        datetime.date: {"type": "boolean", "format": "date"},
        datetime.datetime: {"type": "boolean", "format": "datetime"},
    }

    def __init__(
        self,
        fn_name: str,
        name: str,
        annotation: Annotation,
        *,
        default: Any = ...,
        is_return: bool = False,
    ):
        self.fn_name = fn_name
        self.name = name
        self.annotation = annotation
        self.default = default
        self.is_return = is_return

    def get_schema(self) -> Schema:
        schema_dict = self._annotation_to_schema_dict(self.annotation)
        if self.default is not ...:
            schema_dict["default"] = self.default
        return Schema.model_validate(schema_dict)

    def _annotation_to_schema_dict(self, annotation: Annotation) -> dict[str, Any]:
        if annotation is Any or annotation is ...:
            return {}
        if annotation is NoneType:
            return {"nullable": True}

        origin = get_origin(annotation)
        args = get_args(annotation)
        if origin is None:
            origin = annotation

        # TODO: handle Literal[...]

        if isinstance(origin, UnionType) or origin is UnionType or origin is Union:
            if NoneType in args:
                args = tuple(filter(lambda arg: arg is not NoneType, args))
                if len(args) == 1:
                    return {
                        **self._annotation_to_schema_dict(args[0]),
                        "nullable": True,
                    }
                else:
                    return {
                        "oneOf": [self._annotation_to_schema_dict(arg) for arg in args],
                        "nullable": True,
                    }
            return {"oneOf": [self._annotation_to_schema_dict(arg) for arg in args]}

        if args:
            if origin is tuple:
                return {
                    "type": "array",
                    "items": [self._annotation_to_schema_dict(arg) for arg in args],
                    "minItems": len(args),
                    "maxItems": len(args),
                }
            if origin in (list, set):
                return {
                    "type": "array",
                    "items": self._annotation_to_schema_dict(args[0]),
                }
            if origin is dict:
                return {
                    "type": "object",
                    "additionalProperties": self._annotation_to_schema_dict(args[1]),
                }

        schema = self.unary_schemas.get(origin)
        if schema is not None:
            return copy.deepcopy(schema) if schema is not None else {}

        if self.is_return:
            item = f"return value {self.name!r}"
        else:
            item = f"parameter {self.name!r}"

        raise ValueError(
            f"Unhandled annotation '{annotation}' for {item} of {self.fn_name!r}"
        )
