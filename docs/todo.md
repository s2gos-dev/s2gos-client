# DTE-S2GOS client To-Dos

The DTE-S2GOS client is currently under development.
Given here are the issues that will be addressed next.

## Repo/package setup

* Move all source code into `src` folder.
* Use either `uv` or `pixi` for package and environment management.
* Align `ruff` settings with other [S2GOS repos](https://github.com/s2gos-dev).


## Client implementation

General design

- We need two API Client API versions: sync and async
  - generate them using [`httpx`](https://github.com/encode/httpx), which 
    should replace currently used `requests`
  - use the async version in the Client GUI 

Enhance the API Client

- Consider generating a higher-level client from the 
  OGC API Processes descriptions
- Address the user-facing issues given under [Code generation](#code_generation)

Enhance the GUI Client

- `show_jobs()`: 
  - **DONE**: use `Tabulator`
  - Add an action row with actions applicable to the current table selection
  - Actions:
    - ⬇️ get job result(s)
    - ✖️ cancel accepted/running job(s)
    - ♻️️ restart dismissed/failed job(s)
    - ❌ delete successful/dismissed/failed job(s)
- `show_submitter()`
- `show_processes()`
- `show_process(process_id: str = None, job_id: str = None, editable: bool = True)`
- `show_job(job_id: str = None)`

Implement CLI commands
- `show_processes()`
- `show_process(process_id: str = None, job_id: str = None, editable: bool = True)`
- `show_jobs()` with cancel option
- `show_job(job_id: str = None)`

## Server implementation

* **DONE**: Implement local service that can invoke any Python function
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

* We currently have no error management in client. 
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
5. Generated JSON is too verbose. Avoid including `None` fields and 
   fields that have default values.

- Adjust `s2gos/common/openapi.yaml` to fix the above and/or
- Configure `datamodel-code-generator` to fix the above and/or
- Use [openapi-pydantic](https://github.com/mike-oakley/openapi-pydantic)
  - Use `openapi_pydantic.Schema`, `openapi_pydantic.Reference`, etc. in generated code
  - Use `openapi_pydantic.OpenAPI` for representing `s2gos/common/openapi.yaml` in 
    the generators
