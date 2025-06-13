# TODO

## Observed Errors

1. `python orchestrator.py --help` fails due to missing module `pandas`.
2. `make test` fails at `setup.sh` because it tries to activate `env-as`, which is not created.

## Action Items

- Update environment setup to ensure required Python packages (e.g., pandas) are installed before running the orchestrator.
- Modify `setup.sh` to either create `env-as` or skip the activation test if it is not needed.

## Status

The setup script now creates the `env-tpa` environment by default and installs all required packages using prebuilt wheels. An optional `env-as` can be created for Auto-Sklearn (Python ≤3.10). Activation scripts use the standard `venv` mechanism so `python orchestrator.py --help` works after running `./setup.sh` and activating the environment.

