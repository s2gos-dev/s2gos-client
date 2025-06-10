# DTE-S2GOS Python client

A Python client for the ESA DTE-S2GOS synthetic scene generator service

## Development

Create a new environment using `conda` or `mamba`

```commandline
mamba env create -f ./environment.yml 
conda activate s2gos
pip install -ve . 
```
### Formatting

```commandline
isort .
```

```commandline
ruff format 
```

### Linting

```commandline
ruff check
```

### Testing & Coverage

```commandline
pytest --cov s2gos --cov-report html tests
```

### Code generation

Generate [pydantic](https://docs.pydantic.dev/) models in `s2gos/common/models.py` 
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

### Documentation generation

Generate client CLI reference documentation in `docs/cli.md`:

```commandline
python -m generators.gen_client_cli_md
```

### Run server

```commandline
s2gos-server dev
```

or using FastAPI CLI

```commandline
$ fastapi dev s2gos/server/main.py
```

### Run client Python API

```python
from s2gos.client.api import Client

client = Client()
client.get_landing_page()
```

### Run client CLI

```commandline
$ s2gos --help
```

### Run client GUI 

Run via panel server:

```commandline
$ panel serve  --show --dev ./examples/demo.py
```
