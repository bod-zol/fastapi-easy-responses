# Contributing

## Development

This project was created with [uv](https://github.com/astral-sh/uv) project manager. So the easiest way to develop it is to install uv, then run

```bash
uv sync
```

in the project root folder, which will automatically install all required dependencies to the virtual environment uv provides.

See more at [uv guides](https://docs.astral.sh/uv/guides/projects/).

### Rules of thumb

Add new files to the `fastapi_easy_responses` folder.

Add new tests to the `tests` folder.

Add new dependencies by running

```bash
uv add foobar
# or for development-only dependencies
uv add --dev foobar
```

and commit both the changed [pyproject.toml](/pyproject.toml) and [uv.lock](/uv.lock) files.

### Pre-commit hooks

Also, after cloning the repo, run

```bash
uv run pre-commit install
uv run pre-commit run --all-files
```

for your convenience. This will allow running the linter and auto-formatter before every commit.

These checks also [run](/.github/workflows/ci.yml) for every pull request and after pushes to master.

## Tests

Run

```bash
uv run pytest
```

to run the tests.
