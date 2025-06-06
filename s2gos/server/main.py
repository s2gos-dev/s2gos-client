#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from .app import app
from . import routes

from .impl.local_service import LocalService
from .provider import ServiceProvider

# TODO: should use env var (in .env) to configure actual service to be used
ServiceProvider.set_instance(LocalService())

__all__ = ["app", "routes"]
