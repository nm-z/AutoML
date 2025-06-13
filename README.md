# AutoML

## Quick Setup

**One-command setup** - Run this to get everything working instantly:

```bash
./setup.sh
```

This automatically sets up a `pyenv` environment named `automl-harness` and installs all dependencies (including `pandas`). After running it, activate the environment before using the orchestrator:

```bash
pyenv activate automl-harness
```

If you prefer to manage the environment yourself, install the required packages first after activating your `pyenv` environment:

```bash
pip install -r requirements.txt
```
This step ensures modules like `pandas` are available before running `orchestrator.py`.

> **Note**
> 
> The AutoGluon engine depends on the `autogluon.tabular` package. If this library is missing, `autogluon_wrapper.py` falls back to a simple `LinearRegression`, which severely limits model quality. Run `./setup.sh` or the `pip install` command above to install the full AutoGluon dependencies and avoid the fallback.

## Git Repository Structure

This repository has three main branches:
- **`main`** - Primary development branch
- **`master`** - Mirror of main branch  
- **`V1.1`** - Version 1.1 feature branch

## Python Environment Management

This project uses `pyenv` to manage Python versions and virtual environments.

### Quick Environment Usage

```bash
# Activate the AutoML Harness environment
pyenv activate automl-harness

# Deactivate the environment
pyenv deactivate
```

### Multi-Python Setup (3.10 + 3.11)

To run **Auto-Sklearn** and **TPOT** alongside **AutoGluon** without Docker,
create two `pyenv` environments. Python 3.10 is needed for Auto-Sklearn and,
in many cases, TPOT, while Python 3.11 can run the orchestrator and
AutoGluon.

```bash
pyenv install 3.10.14
pyenv install 3.11.9

pyenv virtualenv 3.10.14 automl-py310
pyenv virtualenv 3.11.9 automl-py311

pyenv activate automl-py310
pip install --upgrade pip
pip install -r requirements.txt
pyenv deactivate

pyenv activate automl-py311
pip install --upgrade pip
# Comment out auto-sklearn and tpot in requirements.txt if needed
pip install -r requirements.txt
pyenv deactivate
```

Run the orchestrator in the **automl-py311** environment and spawn
Auto-Sklearn and TPOT via `pyenv exec python3.10`:

```python
# orchestrator.py snippet
subprocess.run(["pyenv", "exec", "python3.10", "tpot_worker.py", "input.csv", "output.csv"])
subprocess.run(["pyenv", "exec", "python3.10", "autosklearn_worker.py", "input.csv", "output.csv"])
```

For convenience, a small shell script can automate the sequence:

```bash
export PYENV_VERSION=automl-py311
python orchestrator.py --all
```

:::task-stub{title="Switch to PYENV_VERSION if pyenv exec fails"}
Set `PYENV_VERSION=automl-py310` before calling `python tpot_worker.py` or
`python autosklearn_worker.py`. This ensures the scripts run in the correct
environment if `pyenv exec` is unavailable.
:::

### Python 3.13 Compatibility Notes

The setup script supports Python 3.13 but with limitations:
- **Auto-sklearn**: Not compatible with Python 3.13 (will be skipped)
- **AutoGluon**: Not compatible with Python 3.13 (will be skipped)  
- **TPOT**: Works with Python 3.13 with compatibility warnings
- **XGBoost/LightGBM**: Generally compatible with Python 3.13

For best compatibility, install Python 3.11 using `pyenv`:
```bash
pyenv install 3.11.9
```

### Manual Installation (if setup.sh fails)

```bash
# Install Python 3.11 using pyenv if not already present
pyenv install 3.11.9

# Create the pyenv virtual environment
pyenv virtualenv 3.11.9 automl-harness

# Activate the environment
pyenv activate automl-harness

# Install dependencies
pip install --upgrade pip
pip install --only-binary=:all: -r requirements.txt

# Deactivate the environment
pyenv deactivate
```

## Running the Orchestrator

```bash
# Activate the environment
pyenv activate automl-harness

# Run the orchestrator (AutoGluon, Auto-Sklearn, and TPOT all run)
python orchestrator.py --all --time 3600 \
  --data DataSets/3/predictors_Hold\ 1\ Full_20250527_151252.csv \
  --target DataSets/3/targets_Hold\ 1\ Full_20250527_151252.csv

# The orchestrator automatically runs Auto-Sklearn, TPOT and AutoGluon
# together. The `--all` flag is optional but included here for clarity.
pyenv deactivate
```

All orchestrations run **AutoGluon**, **Auto-Sklearn**, and **TPOT** simultaneously. The `--all` flag ensures every run evaluates each engine before selecting a champion.

## Project Structure

```
AutoML-Harness/
├── orchestrator.py              # Main entry point
├── setup.sh                     # One-command setup script
├── engines/                     # AutoML engine wrappers
├── components/                  # Preprocessors and models
├── DataSets/                    # Input datasets
├── 05_outputs/                  # Generated artifacts and results
└── requirements.txt             # Base dependencies
```

## Output Artifacts

All runs generate artifacts in `05_outputs/<dataset_name>/`:
- **`*_champion.pkl`** - Trained pipeline for each engine
- **`metrics.json`** - Comprehensive 5×3 CV performance metrics  
- **`*.log`** - Detailed execution logs

## System Requirements

- Linux (recommended) or macOS
- Python 3.11+ (recommended) or Python 3.13 (with limitations)
- 8GB+ RAM for larger datasets

- Build tools (`build-essential` on Ubuntu, `base-devel` on Arch) 
## Log Aggregation

This project previously supported an ELK stack configuration for log aggregation.
However, this is no longer directly supported in the `pyenv-only` setup. For log aggregation, consider setting up a separate logging solution that integrates with Python's logging module.

## Running in Docker with Persistent Logs

This project no longer provides direct Docker support in the `pyenv-only` branch. For Dockerized deployments, please refer to other branches or configurations that explicitly include Dockerfiles and docker-compose configurations.

## Troubleshooting

- **Environment not activated** – If you encounter `ModuleNotFoundError` or similar issues,
  activate the pyenv environment:

  ```bash
  pyenv activate automl-harness
  ```

  Deactivate the current environment at any time using `pyenv deactivate`.

- **Setup problems** – If `./setup.sh` fails, follow the instructions in the
  *Manual Installation* section to set up the `pyenv` environment manually and
  install the required packages.

- **Python version incompatibilities** – AutoGluon and Auto-Sklearn are skipped
  on Python 3.13. Use Python 3.11 for full functionality.

## License

This project is licensed under the [MIT License](LICENSE).

