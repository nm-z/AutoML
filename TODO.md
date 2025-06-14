# TODO

## Completed Tasks
- Added run_all.sh for 60-second smoke test.
- Git LFS setup completed, including tracking of `.pkl`, `.json`, `DataSets/`, and `05_outputs/` directories. Git history has been cleaned to properly track large files.
- `orchestrator.py` `AttributeError` for duration calculation fixed.
- Smoke test for `orchestrator.py` passed successfully. All engines (AutoGluon, Auto-Sklearn, TPOT) executed, data loaded, split, and artifacts saved.
- Resolved scikit-learn version conflict by specifying `scikit-learn>=1.4.2,<1.6` so Auto-Sklearn and TPOT install together.
- Setup script now creates `automl-py310` and `automl-py311` pyenv environments automatically.
- Added `--tree` flag to `orchestrator.py` to display artifact directory trees and implemented tests verifying the output.
- Reviewed and processed 9 pull requests: accepted 4 valuable PRs (run_all.sh, offline setup docs, tree flag, pyenv migration) and declined 5 problematic PRs (regressions, breaking changes, duplicates).
- Added offline setup documentation for restricted network environments.
- Completed systematic PR review and cleanup: processed all open PRs (13 total), closed duplicates and problematic PRs, maintained clean repository state.
- Fixed `run_all.sh` so it initializes pyenv when run in a non-interactive shell.
- Completed systematic review of PRs #94-#97: merged PR #97 (pyenv initialization fix) and rejected PRs #94-#96 (all attempted to revert the pyenv improvements).

## Remaining Action Items

- Update environment setup to ensure required Python packages (e.g., pandas) are installed before running the orchestrator.
- Modify `setup.sh` to skip automl-py310 creation gracefully when Python 3.10 is unavailable.
- Enhance console logs using `rich.tree` so run progress is shown as a clear tree.
- Verify `run_all.sh` smoke test passes after updating dependencies.
- Revise setup or CI to ensure required packages like `rich` install reliably without manual intervention.
- Bundle prebuilt wheels or configure a local PyPI mirror so `make test` can run without internet access.
- Apply the `deactivate` to `pyenv deactivate` fix from rejected PR #96 to `setup.sh`.
- Detect missing `pyenv-virtualenv` plugin during setup and provide instructions to install it when `pyenv virtualenv` is unavailable.

## Status

The setup script now creates `automl-py310` and `automl-py311` pyenv environments for improved version management. Recent PR review cycle completed with significant improvements to environment management, testing capabilities, and documentation. All current PRs have been processed and repository is in clean state with proper pyenv initialization in place.

