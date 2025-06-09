#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import s2gos.client.gui as s2g_gui

schema = {
    "title": "S2GOS Job Configuration",
    "type": "object",
    "properties": {
        "dataset": {
            "type": "string",
            "enum": ["Landsat-8", "Sentinel-2", "MODIS"],
            "title": "Dataset",
        },
        "region": {
            "type": "array",
            "title": "Region of Interest",
            "format": "bbox",
            "items": {"type": "number"},
            "minItems": 4,
            "maxItems": 4,
        },
        "start_date": {"type": "string", "format": "date", "title": "Start Date"},
        "end_date": {"type": "string", "format": "date", "title": "End Date"},
        "cloud_threshold": {
            "type": "number",
            "minimum": 0,
            "maximum": 100,
            "title": "Max Cloud Coverage (%)",
        },
        "include_ndvi": {"type": "boolean", "title": "Include NDVI in Output"},
    },
    "required": ["dataset", "region", "start_date", "end_date"],
}

gui = s2g_gui.create(schema)
gui.servable()
