# Exploring code generation options

With datamodel-codegen (`mamba install datamodel-code-generator`)

```commandline
datamodel-codegen --input ".\s2gos\server\openapi.yaml" --input-file-type "openapi" --output "models.py" --output-model-type "pydantic_v2.BaseModel" --formatters "ruff-format" --use-union-operator --target-python-version "3.13"
```

With openapi-generator 

```commandline
openapi-generator-cli generate -i s2gos/server/openapi.yaml -g python-fastapi -o ./generated/server 
openapi-generator-cli generate -i s2gos/server/openapi.yaml -g python -o ./generated/client 
```
