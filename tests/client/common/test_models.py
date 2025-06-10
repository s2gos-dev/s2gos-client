#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import inspect
from enum import Enum
from unittest import TestCase

from pydantic import BaseModel

import s2gos.common.models as s2g_models

REQUIRED_ENUMS = {
    "Crs",
    "JobControlOptions",
    "StatusCode",
}

REQUIRED_MODELS = {
    "ConfClasses",
    "Exception",
    "Execute",
    "Format",
    "InputDescription",
    "JobList",
    "LandingPage",
    "Link",
    "Metadata",
    "Output",
    "OutputDescription",
    "Process",
    "ProcessList",
    "ProcessSummary",
    "QualifiedInputValue",
    "Reference",
    "Schema",
    "StatusInfo",
}


class ModelsTest(TestCase):
    def test_enums(self):
        all_enums = set(
            name
            for name, obj in inspect.getmembers(s2g_models, inspect.isclass)
            if issubclass(obj, Enum)
        )
        self.assertSetEqual(set(), REQUIRED_ENUMS - all_enums)

    def test_models(self):
        all_models = set(
            name
            for name, obj in inspect.getmembers(s2g_models, inspect.isclass)
            if issubclass(obj, BaseModel)
        )

        self.assertSetEqual(set(), REQUIRED_MODELS - all_models)
