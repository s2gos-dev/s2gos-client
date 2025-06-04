#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from pathlib import Path
from dataclasses import dataclass
from typing import Optional

import yaml

from s2gos.client.defaults import DEFAULT_CONFIG_PATH

# TODO: use pydantic BaseModel instead of @dataclass


@dataclass
class Config:
    user_name: str
    access_token: str
    server_url: str

    @classmethod
    def get(cls, config_path: Path = DEFAULT_CONFIG_PATH) -> Optional["Config"]:
        if not config_path.exists():
            return None
        with config_path.open("rt") as f:
            config = yaml.load(f, Loader=yaml.SafeLoader)
            return Config(**config)

    def write(self, config_path: Path = DEFAULT_CONFIG_PATH) -> Path:
        config_path.parent.mkdir(exist_ok=True)
        with config_path.open("wt") as f:
            f.write(f"user_name: {self.user_name}\n")
            f.write(f"access_token: {self.access_token}\n")
            f.write(f"server_url: {self.server_url}\n")
        return config_path
