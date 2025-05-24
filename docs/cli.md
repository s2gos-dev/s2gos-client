# CLI Reference

## Main Command

```
Usage: s2gos [OPTIONS] COMMAND [ARGS]...

  Client tool for the ESA synthetic scene generator service DTE-S2GOS.

  The tool provides commands for managing processing request templates,
  processing requests, processing jobs, and gets processing results.

  You can use shorter command name aliases, e.g., use command name "vr" instead
  of "validate-request", or "lt" instead of "list-templates".

Options:
  --help  Show this message and exit.

Commands:
  configure         Configure the S2GOS client.
  get-template      Get a processing request template.
  list-templates    List available processing request templates.
  validate-request  Validate a processing request.
  submit-request    Submit a processing request.
  cancel-jobs       Cancel running processing jobs.
  poll-jobs         Poll the status of processing jobs.
  get-results       Get processing results.
```

## Commands

### `configure`

```
Usage: s2gos configure [OPTIONS]

  Configure the S2GOS client.

Options:
  --user TEXT
  --token TEXT
  --url TEXT
  --help        Show this message and exit.
```

### `get-template`

```
Usage: s2gos get-template [OPTIONS] TEMPLATE_NAME

  Get a processing request template.

Options:
  --request TEXT
  --help          Show this message and exit.
```

### `list-templates`

```
Usage: s2gos list-templates [OPTIONS]

  List available processing request templates.

Options:
  --help  Show this message and exit.
```

### `validate-request`

```
Usage: s2gos validate-request [OPTIONS]

  Validate a processing request.

Options:
  --name TEXT
  --help       Show this message and exit.
```

### `submit-request`

```
Usage: s2gos submit-request [OPTIONS]

  Submit a processing request.

Options:
  --name TEXT
  --help       Show this message and exit.
```

### `cancel-jobs`

```
Usage: s2gos cancel-jobs [OPTIONS] [JOB_IDS]...

  Cancel running processing jobs.

Options:
  --help  Show this message and exit.
```

### `poll-jobs`

```
Usage: s2gos poll-jobs [OPTIONS] [JOB_IDS]...

  Poll the status of processing jobs.

Options:
  --help  Show this message and exit.
```

### `get-results`

```
Usage: s2gos get-results [OPTIONS] [JOB_IDS]...

  Get processing results.

Options:
  --help  Show this message and exit.
```
