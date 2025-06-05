# DTE-S2GOS Python client

A Python client for the ESA DTE-S2GOS synthetic scene generator service

## Development

Create a new environment using `conda` or `mamba`

```commandline
mamba env create -f ./environment.yml 
conda activate s2gos
pip install -ve . 
```

### Server

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
