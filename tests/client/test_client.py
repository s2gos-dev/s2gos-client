#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from unittest import TestCase

from s2gos.client import Client
from s2gos.common.models import (
    ConfClasses,
    JobInfo,
    JobList,
    LandingPage,
    ProcessDescription,
    ProcessList,
    ProcessRequest,
    ProcessResults,
)
from tests.client.helpers import MockTransport


class ClientTest(TestCase):
    def setUp(self):
        self.transport = MockTransport()
        self.client = Client(_transport=self.transport)

    def test_repr_json(self):
        result = self.client._repr_json_()
        self.assertEqual(
            (
                {"server_url": "https://s2gos.testing.eu/api"},
                {"root": "Configuration:"},
            ),
            result,
        )

    def test_get_landing_page(self):
        result = self.client.get_landing_page()
        self.assertIsInstance(result, LandingPage)

    def test_get_conformance_classes(self):
        result = self.client.get_conformance_classes()
        self.assertIsInstance(result, ConfClasses)

    def test_get_processes(self):
        result = self.client.get_processes()
        self.assertIsInstance(result, ProcessList)

    def test_get_process_description(self):
        result = self.client.get_process_description(process_id="gobabeb_1")
        self.assertIsInstance(result, ProcessDescription)

    def test_execute(self):
        result = self.client.execute(
            process_id="gobabeb_1",
            request=ProcessRequest(
                inputs={"bbox": [10, 20, 30, 40]},
                outputs={},
            ),
        )
        self.assertIsInstance(result, JobInfo)

    def test_get_jobs(self):
        result = self.client.get_jobs()
        self.assertIsInstance(result, JobList)

    def test_dismiss(self):
        result = self.client.dismiss("job_12")
        self.assertIsInstance(result, JobInfo)

    def test_get_status(self):
        result = self.client.get_status("job_12")
        self.assertIsInstance(result, JobInfo)

    def test_get_result(self):
        result = self.client.get_result("job_12")
        self.assertIsInstance(result, ProcessResults)
