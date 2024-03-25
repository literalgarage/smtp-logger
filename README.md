# smtp-logger

[![PyPI](https://img.shields.io/pypi/v/smtp-logger.svg)](https://pypi.org/project/smtp-logger/)
[![Tests](https://github.com/literalgarage/smtp-logger/actions/workflows/test.yml/badge.svg)](https://github.com/literalgarage/smtp-logger/actions/workflows/test.yml)
[![Changelog](https://img.shields.io/github/v/release/literalgarage/smtp-logger?include_prereleases&label=changelog)](https://github.com/literalgarage/smtp-logger/releases)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/literalgarage/smtp-logger/blob/main/LICENSE)

Mock SMTP server that logs the emails it receives.

Listens to inbound connections from SMTP clients. Supports a very minimal set of SMTP features, but probably enough that most clients will communicate happily and emails will get "delivered" as expected.

## Why?

This is useful in development, often as part of a `docker-compose.yml`.

There have been a couple cases recently where I wanted to work with an OSS tool that required a configured SMTP server (for instance, to send password reset or login link emails). The tool itself didn't offer an alternative, so creating a simple logging SMTP service seemed like the best way to go.

## Installation via docker

The latest version of `smtp-logger` is packaged in a docker image available at `https://ghcr.io/literalgarage/smtp-logger:latest`.

For instance, to create an `smtp` logger service in your `docker-compose.yml`:

```
smtp:
  image: ghcr.io/literalgarage/smtp-logger:latest
  environment:
    - SMTP_LOGGER_PORT=8025
  ports:
    - "8025:8025"
```

## Installation locally

Install this library using `pip`:

```bash
pip install smtp-logger
```

## Usage

This adds an `smtp-logger` binary.

It accepts only `--host` and `--port` parameters or corresponding (`SMTP_LOGGER_HOST` and `SMTP_LOGGER_PORT`) environment variables, all of which are optional.

The default `SMTP_LOGGER_HOST` is `localhost` and the default `SMTP_LOGGER_PORT` is `8025`.

## Development

This is the simplest SMTP logging implementation that worked for the specific cases I ran into. There are an enormous number of basic and advanced SMTP features this server doesn't yet support. Its handling of `content-transfer-encoding`s is weak at the moment. It doesn't support TLS. etc.

To contribute to this library, first checkout the code. Then create a new virtual environment:

```bash
cd smtp-logger
python -m venv .venv
source .venv/bin/activate
```

Now install the dependencies and test dependencies:

```bash
pip install -e '.[dev]'
```

To run tests:

```bash
make test
```

To run a full lint/typecheck/test pass:

```bash
make check
```
