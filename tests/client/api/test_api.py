#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from typing import Literal, Any
from unittest import TestCase

import s2gos.client.api.api as s2g_api
from s2gos.client.api.service import Service
from s2gos.common.models import LandingPage, ConfClasses, ProcessList, Process


class TestService(Service):
    def __init__(self):
        self.call_stack = []

    def call(
        self,
        path: str,
        method: Literal["get", "post", "put", "delete"],
        params: dict[str, Any],
        request: Any,
        return_type: type[object],
    ) -> Any:
        self.call_stack.append(
            dict(
                path=path,
                method=method,
                params=params,
                request=request,
                return_type=return_type,
            )
        )
        return object.__new__(return_type)


class ClientApiTest(TestCase):
    def setUp(self):
        self._old_service = Service.set_default(TestService())

    def tearDown(self):
        Service.set_default(self._old_service)

    @property
    def service(self) -> TestService:
        # noinspection PyTypeChecker
        return Service.default()

    def assert_service_call_ok(self, expected_kwargs: dict[str, Any]):
        self.assertEqual(1, len(self.service.call_stack))
        self.assertEqual(
            expected_kwargs,
            self.service.call_stack[0],
        )

    def test_get_landing_page(self):
        result = s2g_api.get_landing_page()
        self.assert_service_call_ok(
            {
                "path": "/",
                "method": "get",
                "params": {},
                "request": None,
                "return_type": LandingPage,
            }
        )
        self.assertIsInstance(result, LandingPage)

    def test_get_conformance_classes(self):
        result = s2g_api.get_conformance_classes()
        self.assert_service_call_ok(
            {
                "path": "/conformance",
                "method": "get",
                "params": {},
                "request": None,
                "return_type": ConfClasses,
            }
        )
        self.assertIsInstance(result, ConfClasses)

    def test_get_processes(self):
        result = s2g_api.get_processes()
        self.assert_service_call_ok(
            {
                "path": "/processes",
                "method": "get",
                "params": {},
                "request": None,
                "return_type": ProcessList,
            }
        )
        self.assertIsInstance(result, ProcessList)

    def test_get_process_description(self):
        result = s2g_api.get_process_description(process_id="gobabeb_1")
        self.assert_service_call_ok(
            {
                "path": "/processes/{processID}",
                "method": "get",
                "params": {"processID": "gobabeb_1"},
                "request": None,
                "return_type": Process,
            }
        )
        self.assertIsInstance(result, Process)
