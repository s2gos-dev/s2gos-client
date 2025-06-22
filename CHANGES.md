## Changes in version 0.0.4 (in development)

* Added basic request submit form to client GUI.

## Changes in version 0.0.5 (in development)

- Changed `s2gos/common/openapi.yaml`
  - renamed `exception` component into `apiError`
  - renamed `statusInfo` component into `jobInfo`
  - extended `StatusInfo` by `traceback`

- Renamed models in `s2gos.common.models`:
  - `Exception` --> `ApiError`
  - `StatusInfo` --> `JobInfo`


## Changes in version 0.0.4 (not released)

* Added basic submit form to GUI client: `s2gos.client.gui.Client.show_submitter()`

## Changes in version 0.0.3 (not released)

* Server now has a new option `--service` to specify the service implementation.
  It specifies an instance of an implementation of `s2gos.server.service.Service`, 
  e.g., `s2gos.server.services.testing:service`. Or use env var `S2GOS_SERVICE`.
* Added a useful process server impl. `LocalService` for local Python user
  functions in `s2gos.server.services.local`:
  * Uses a new decorator `@service.process_info` to register user functions.
  * Find example in  `s2gos/server/services/testing.py`.
* In GUI client prototype, changed job table to have an action row instead 
  of action table columns.
* Added `docs/todo.md`

## Changes in version 0.0.2 (not released)

* Reorganized package
* Started code generation for models, client, and server
* Added basic FastAPI server, added server CLI `s2gos-server`
* Using dummy implementation for the S2GOS service
* Using `Typer` instead of `Click`
* Added pretty rendering of model object in Jupyter notebooks

## Version 0.0.1 (not released) 

Initial setup.
