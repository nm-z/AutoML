# TODO

## Completed Tasks

- Git LFS setup completed, including tracking of `.pkl`, `.json`, `DataSets/`, and `05_outputs/` directories. Git history has been cleaned to properly track large files.
- `orchestrator.py` `AttributeError` for duration calculation fixed.
- Smoke test for `orchestrator.py` passed successfully. All engines (AutoGluon, Auto-Sklearn, TPOT) executed, data loaded, split, and artifacts saved.
- Removed Docker and venv related files and configurations. Project now exclusively uses pyenv for environment management.
- Updated `setup.sh` to configure and use a `pyenv` environment named `automl-harness`.
- Updated `README.md` to reflect the `pyenv-only` setup and provide new instructions.

## Remaining Action Items

- Enhance console logs using `rich.tree` so run progress is shown as a clear tree.
- Add a `--tree` flag to `orchestrator.py` to optionally print artifact directories in tree form.
- Create tests verifying tree-formatted output appears when the flag is used.

## Status

The setup script now creates the `automl-harness` pyenv environment by default and installs all required packages. Activation is done via `pyenv activate automl-harness`.

- Investigate auto-sklearn installation failure on Python 3.11 and document workaround (e.g., use Python 3.9 or compile scikit-learn 0.24).
