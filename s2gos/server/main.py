#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import importlib
import os

from . import routes
from .app import app
from .impl.local_service import LocalService
from .provider import ServiceProvider


def get_service():
    service_class_spec = os.environ.get("S2GOS_SERVICE_CLASS")
    if service_class_spec is None:
        # TODO: replace by true S2GOS service
        return LocalService()
    else:
        module_name, class_name = service_class_spec.split(":", maxsplit=1)
        module = importlib.import_module(module_name)
        service_cls = getattr(module, class_name)
        return service_cls()


ServiceProvider.set_instance(get_service())

__all__ = ["app", "routes"]
