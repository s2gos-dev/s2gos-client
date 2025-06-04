# DTE-S2GOS Python client

A Python client for the ESA DTE-S2GOS synthetic scene generator service

## Development

Create a new environment using `conda` or `mamba`

```commandline
mamba env create -f ./environment.yml 
conda activate s2gos
pip install -ve . 
```

### Python API

```python
import s2gos.client.api as s2g_api

s2g_api.get_landing_page()
```


### CLI

```commandline
s2gos --help
```

### GUI 

Run via panel server:

```commandline
panel serve  --show --dev ./examples/demo.py
```
