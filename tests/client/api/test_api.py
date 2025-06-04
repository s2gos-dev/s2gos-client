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
        return_type: type[object],
    ) -> Any:
        self.call_stack.append(
            dict(path=path, method=method, params=params, return_type=return_type)
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

    def test_get_landing_page(self):
        result = s2g_api.get_landing_page()
        self.assertIsInstance(result, LandingPage)

    def test_get_conformance_classes(self):
        result = s2g_api.get_conformance_classes()
        self.assertEqual(1, len(self.service.call_stack))
        self.assertEqual(
            {
                "path": "/conformance",
                "method": "get",
                "params": {},
                "return_type": ConfClasses,
            },
            self.service.call_stack[0],
        )
        self.assertIsInstance(result, ConfClasses)

    def test_get_processes(self):
        result = s2g_api.get_processes()
        self.assertEqual(1, len(self.service.call_stack))
        self.assertEqual(
            {
                "path": "/processes",
                "method": "get",
                "params": {},
                "return_type": ProcessList,
            },
            self.service.call_stack[0],
        )
        self.assertIsInstance(result, ProcessList)

    def test_get_process_description(self):
        result = s2g_api.get_process_description(process_id="gobabeb_1")
        self.assertEqual(1, len(self.service.call_stack))
        self.assertEqual(
            {
                "path": "/processes/{processID}",
                "method": "get",
                "params": {"processID": "gobabeb_1"},
                "return_type": Process,
            },
            self.service.call_stack[0],
        )
        self.assertIsInstance(result, Process)
