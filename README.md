# DTE-S2GOS Python client

A Python client for the ESA DTE-S2GOS synthetic scene generator service

## Development

Create a new environment using `conda` or `mamba`

```commandline
mamba env create -f ./environment.yml 
conda activate s2gos
pip install -ve . 
```

### Code generation

Generate models in `s2gos/common/models.py` 
(uses [datamodel-code-generator](https://koxudaxi.github.io/datamodel-code-generator/)):

```commandline
python -m generators.gen_models
```

Generate client API in `s2gos/client/api/client.py`:

```commandline
python -m generators.gen_client
```

Generate server routes in `s2gos/server/routes.py` and 
service interface in `s2gos/server/service.py`:

```commandline
python -m generators.gen_server
```


With datamodel-codegen (`mamba install datamodel-code-generator`)

```commandline
datamodel-codegen --input ".\s2gos\server\openapi.yaml" --input-file-type "openapi" --output "models.py" --output-model-type "pydantic_v2.BaseModel" --formatters "ruff-format" --use-union-operator --target-python-version "3.13"
```

With openapi-generator 

```commandline
openapi-generator-cli generate -i s2gos/server/openapi.yaml -g python-fastapi -o ./generated/server 
openapi-generator-cli generate -i s2gos/server/openapi.yaml -g python -o ./generated/client 
```

### Server

```commandline
s2gos-server dev
```

or using FastAPI CLI

```commandline
$ fastapi dev s2gos/server/main.py
```

### Client Python API

```python
from s2gos.client.api import Client

client = Client()
client.get_landing_page()
```

### Client CLI

```commandline
$ s2gos --help
```

### Client GUI 

Run via panel server:

```commandline
$ panel serve  --show --dev ./examples/demo.py
```
