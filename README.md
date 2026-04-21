# pytrade

Public monorepo containing the core PyTrade trading framework packages.

## Packages

| Package | Path | Description |
|---|---|---|
| `pytrade` | `src/pytrade/` | Core abstractions — strategies, indicators, instruments, broker interfaces |
| `pytrade-backtest` | `src/pytrade-backtest/` | Backtesting engine for running strategies against historical CSV data |
| `pytrade-oanda` | `src/pytrade-oanda/` | Oanda brokerage adapter implementing `IClient` |

## Local Development

```bash
# Install all packages in editable mode
poetry install

# Run unit tests
make test

# Run a specific test suite
poetry run pytest tests/unit/pytrade
poetry run pytest tests/unit/backtest
poetry run pytest tests/unit/oanda

# Lint
make lint

# Auto-format
make reformat
```

## Building Sub-Packages

Each sub-package can be built and published independently:

```bash
make build-pytrade
make build-pytrade-backtest
make build-pytrade-oanda
# or all at once:
make build-all
```

## Dependency Graph

```
src/pytrade           (standalone — numpy, pandas)
src/pytrade-backtest  (depends on: pytrade, plotly, progressbar2)
src/pytrade-oanda     (depends on: pytrade, v20-python, pyyaml)
```
