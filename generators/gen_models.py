#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from generators.common import (
    S2GOS_PATH,
    OPEN_API_PATH,
)
import datamodel_code_generator as dcg


MODELS_PATH = S2GOS_PATH / "common" / "models.py"


def main():
    dcg.generate(
        input_=OPEN_API_PATH,
        input_file_type=dcg.InputFileType.OpenAPI,
        output_model_type=dcg.DataModelType.PydanticV2BaseModel,
        output=MODELS_PATH,
    )


if __name__ == "__main__":
    main()
