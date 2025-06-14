# TODO

## Completed Tasks
- Added run_all.sh for 60-second smoke test.

- Git LFS setup completed, including tracking of `.pkl`, `.json`, `DataSets/`, and `05_outputs/` directories. Git history has been cleaned to properly track large files.
- `orchestrator.py` `AttributeError` for duration calculation fixed.
- Smoke test for `orchestrator.py` passed successfully. All engines (AutoGluon, Auto-Sklearn, TPOT) executed, data loaded, split, and artifacts saved.
- Resolved scikit-learn version conflict by specifying `scikit-learn>=1.4.2,<1.6` so Auto-Sklearn and TPOT install together.
- Setup script now creates `env-as` and `env-tpa` virtual environments. Migration to pyenv is planned but not yet complete.
- Added `--tree` flag to `orchestrator.py` to display artifact directory trees and implemented tests verifying the output.

## Remaining Action Items

- Update environment setup to ensure required Python packages (e.g., pandas) are installed before running the orchestrator.
- Modify `setup.sh` to skip `env-as` creation gracefully when Python 3.10 is unavailable.
- Migrate `setup.sh` to use pyenv for environment creation.
- Enhance console logs using `rich.tree` so run progress is shown as a clear tree.
- Verify `run_all.sh` smoke test passes after updating dependencies.
- Add a missing `run_all.sh` script to launch the orchestrator with all three engines for a quick smoke test.
- Revise setup or CI to ensure required packages like `rich` install reliably without manual intervention.
- Bundle prebuilt wheels or configure a local PyPI mirror so `make test` can run without internet access.

## Status

The setup script currently creates `env-as` and `env-tpa` virtual environments. A pyenv-based workflow is planned but not finalized.

