#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from unittest import TestCase

from s2gos.common.models import Process
from s2gos.server.local.process.registry import ProcessRegistry
from s2gos.server.local.process.decorator import process


class DecorateProcessTest(TestCase):
    def test_decorate(self):
        registry = ProcessRegistry()

        foo_process = registry.get_process("foo")
        self.assertIsNone(foo_process)

        @process(id="foo", version="1.4.2", _registry=registry)
        def f(x: bool, y: int) -> float:
            return 2 * y if x else y / 2

        foo_process = registry.get_process("foo")
        self.assertIsInstance(foo_process, Process)
        self.assertEqual("foo", foo_process.id)
        self.assertEqual("1.4.2", foo_process.version)

        bar_process = registry.get_process("bar")
        self.assertIsNone(bar_process)
