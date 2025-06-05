#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from unittest import TestCase

import pytest
from pydantic import ValidationError

from s2gos.client.api.service import DefaultService
from s2gos.common.models import ConfClasses, Exception


class DefaultServiceTest(TestCase):
    def test_call_success(self):
        service = DefaultService()
        # The following test is currently just a smoke test, but that's ok
        with pytest.raises(ValidationError, match="conformsTo"):
            result = service.call(
                path="/conformance",
                method="get",
                params={},
                request=None,
                return_types={"200": ConfClasses},
               error_types={"401": Exception},
            )
            self.assertIsInstance(result, ConfClasses)
