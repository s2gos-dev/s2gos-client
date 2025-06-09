#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from typing import Any, Literal
from unittest import TestCase

from pydantic import BaseModel

from s2gos.client.api import Client
from s2gos.client.api.transport import Transport
from s2gos.common.models import (
    ConfClasses,
    Exception,
    LandingPage,
    Process,
    ProcessList,
)


class TestTransport(Transport):
    def __init__(self):
        self.call_stack = []

    def call(
        self,
        path: str,
        method: Literal["get", "post", "put", "delete"],
        path_params: dict[str, Any],
        query_params: dict[str, Any],
        request: BaseModel | None,
        return_types: dict[str, type | None],
        error_types: dict[str, type | None],
    ) -> Any:
        self.call_stack.append(
            dict(
                path=path,
                method=method,
                path_params=path_params,
                query_params=query_params,
                request=request,
                return_types=return_types,
                error_types=error_types,
            )
        )
        return_type = return_types["200"]
        # noinspection PyTypeChecker
        return object.__new__(return_type) if return_type is not None else None


class ClientApiTest(TestCase):
    def setUp(self):
        self.transport = TestTransport()
        self.client = Client(_transport=self.transport)

    def assert_transport_ok(self, expected_kwargs: dict[str, Any]):
        self.assertEqual(1, len(self.transport.call_stack))
        self.assertEqual(
            expected_kwargs,
            self.transport.call_stack[0],
        )

    def test_get_landing_page(self):
        result = self.client.get_landing_page()
        self.assert_transport_ok(
            {
                "path": "/",
                "method": "get",
                "path_params": {},
                "query_params": {},
                "request": None,
                "return_types": {"200": LandingPage},
                "error_types": {"500": Exception},
            }
        )
        self.assertIsInstance(result, LandingPage)

    def test_get_conformance_classes(self):
        result = self.client.get_conformance_classes()
        self.assert_transport_ok(
            {
                "path": "/conformance",
                "method": "get",
                "path_params": {},
                "query_params": {},
                "request": None,
                "return_types": {"200": ConfClasses},
                "error_types": {"500": Exception},
            }
        )
        self.assertIsInstance(result, ConfClasses)

    def test_get_processes(self):
        result = self.client.get_processes()
        self.assert_transport_ok(
            {
                "path": "/processes",
                "method": "get",
                "path_params": {},
                "query_params": {},
                "request": None,
                "return_types": {"200": ProcessList},
                "error_types": {},
            }
        )
        self.assertIsInstance(result, ProcessList)

    def test_get_process_description(self):
        result = self.client.get_process_description(process_id="gobabeb_1")
        self.assert_transport_ok(
            {
                "path": "/processes/{processID}",
                "method": "get",
                "path_params": {"processID": "gobabeb_1"},
                "query_params": {},
                "request": None,
                "return_types": {"200": Process},
                "error_types": {"404": Exception},
            }
        )
        self.assertIsInstance(result, Process)
