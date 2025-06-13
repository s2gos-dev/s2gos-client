# DTE-S2GOS client To-Dos

The DTE-S2GOS client is currently under development.
Given here are the issues that will be addressed next.

## Repo/package setup

* Move all source code into `src` folder
* Use either `uv` or `pixi` for package and environment management.


## Client implementation

Enhance the API Client

- Consider generating a higher-level client from the 
  OGC API Processes descriptions
- Address the user-facing issues given under [Code generation](#code_generation)

Enhance the GUI Client

- `show_processes()`
- `show_process(process_id: str = None, job_id: str = None, editable: bool = True)`
- `show_jobs()` with cancel option
- `show_job(job_id: str = None)`

Implement CLI commands
- `show_processes()`
- `show_process(process_id: str = None, job_id: str = None, editable: bool = True)`
- `show_jobs()` with cancel option
- `show_job(job_id: str = None)`

## Server implementation

* Implement local service that can invoke any Python function
* Implement Airflow-based service

## Authentication

* Implement basic authentication using OAuth2, 
  use user_name/access_token from ClientConfig in
  - client 
  - server

## Authorisation

* Define roles & scopes
* Implement accordingly in
  - client 
  - server

## Error handling

* We currently only have no error management in client. 
  Handle ClientException so users understand what went wrong:
  - Python API
  - CLI
  - GUI
* Include server traceback on internal server errors with 500 status

## Code generation

The output of `generators/gen_models` is not satisfying: 

1. Many generated classes are `RootModels` which are inconvenient for users.
2. Basic openAPI constructs like `Schema` or `Reference` should not be  
   generated but reused from predefined ` BaseModel`s.
3. Generated class names like `Exception` clash with predefined Python names.
4. Some generated class names are rather unintuitive, e.g., 
   `Execute` instead of `Request`.

- Adjust `s2gos/common/openapi.yaml` to fix the above and/or
- Configure `datamodel-code-generator` to fix the above and/or
- Use [openapi-pydantic](https://github.com/mike-oakley/openapi-pydantic)
  - Use `openapi_pydantic.Schema`, `openapi_pydantic.Reference`, etc. in generated code
  - Use `openapi_pydantic.OpenAPI` for representing `s2gos/common/openapi.yaml` in 
    the generators
