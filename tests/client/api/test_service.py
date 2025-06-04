#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from unittest import TestCase

import pytest
from pydantic import ValidationError

from s2gos.client.api.service import DefaultService, Service
from s2gos.common.models import ConfClasses


class ServiceTest(TestCase):
    def test_default(self):
        self.assertIsInstance(Service.default(), DefaultService)
        self.assertIs(Service.default(), Service.default())

    def test_set_default(self):
        current = DefaultService()
        last1 = Service.default()
        last2 = Service.set_default(current)
        self.assertIs(last1, last2)
        self.assertIs(current, Service.default())


class DefaultServiceTest(TestCase):
    def test_call_success(self):
        service = DefaultService()
        # The following test is currently just a smoke test, but that's ok
        with pytest.raises(ValidationError, match="conformsTo"):
            result = service.call(
                path="/conformance", method="get", params={}, return_type=ConfClasses
            )
            self.assertIsInstance(result, ConfClasses)
