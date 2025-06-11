#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from s2gos.client import Client as GeneratedClient
from .jobstable import JobsTable


class Client(GeneratedClient):
    def show_jobs(self, interval: float):
        return JobsTable(self.get_jobs, interval=interval).show_jobs()
