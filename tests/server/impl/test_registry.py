#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from unittest import TestCase

from s2gos.server.impl.registry import ProcessRegistry, ProcessRegistryEntry


class ProcessRegistryTest(TestCase):
    def test_register_function(self):
        registry = ProcessRegistry()

        def f(x: bool, y: int) -> float:
            return 2 * y if x else y / 2

        entry1 = registry.register_function(f)
        self.assertIsInstance(entry1, ProcessRegistryEntry)
        self.assertEqual("tests.server.impl.test_registry:f", entry1.process.id)
        self.assertEqual("0.0.0", entry1.process.version)
        self.assertIs(f, entry1.function)

        entry2 = registry.register_function(f, id="foo", version="1.0.1")
        self.assertIsInstance(entry2, ProcessRegistryEntry)
        self.assertEqual("foo", entry2.process.id)
        self.assertEqual("1.0.1", entry2.process.version)
        self.assertIs(f, entry2.function)
