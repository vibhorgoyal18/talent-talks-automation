# Configuration Guide

The framework now relies on a project-root `.env` file (with a checked-in `.env.example`) instead of `config/env.properties`.

## Creating your `.env`

1. Copy `.env.example` to `.env` at the repository root.
2. Update values per environment. Keys follow the pattern `ENV__OPTION`, where `ENV` is `DEFAULT`, `STAGE`, `PROD`, etc., and `OPTION` is the lower-case setting consumed in code (e.g., `BASE_URL`, `BROWSER`).
3. Set `TEST_ENV` environment variable (shell or CI) to switch between sections. When `TEST_ENV` is unset, the loader uses the `DEFAULT` section.

```sh
cp .env.example .env
export TEST_ENV=stage
```

## Example Keys

```
DEFAULT__BASE_URL=https://the-internet.herokuapp.com
DEFAULT__BROWSER=chrome
DEFAULT__IMPLICIT_WAIT=10
DEFAULT__EXPLICIT_WAIT=15
DEFAULT__HEADLESS=false

STAGE__BASE_URL=https://stage.example.com
```

## Access in Code

Use `utils.config_loader.get_config()` to read settings. The loader merges the chosen environment over defaults, so `config.get("base_url")` works regardless of the namespace prefix used in `.env`.
