# AudioStats
[![Coverage Status](https://coveralls.io/repos/github/Olezhich/AudioStats/badge.svg?branch=dev)](https://coveralls.io/github/Olezhich/AudioStats?branch=dev)
[![License](https://img.shields.io/github/license/Olezhich/AudioStats )](https://github.com/Olezhich/AudioStats/blob/main/LICENSE )
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](https://python.org)  

> Statistics Analyser for foobar2000

## Features
- Collecting album and track metadata into db
- Tracking album changes
- Working with `flac` + `cue` music libraries

## Technologies
- `SqlAlchemy orm` for interacting with a db
- `Asyncio` for using async requests via `asyncpg` driver
- `PostgreSQL` as db
