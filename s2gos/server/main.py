#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import importlib

from .app import app
from .impl.local_service import LocalService
from .provider import ServiceProvider

importlib.import_module("s2gos.server.routes")

ServiceProvider.set_instance(LocalService())


__all__ = ["app"]
