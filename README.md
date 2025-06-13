# AutoML Harness

## Quick Setup

**One-command setup** - Run this to get everything working instantly:

```bash
./setup.sh
```

This automatically creates the Python 3.11 environment, installs all dependencies (including `pandas`), and sets up the project structure. After running it, activate the environment before using the orchestrator:

```bash
./activate.sh
```

If you prefer to manage the environment yourself, install the required packages first:

```bash
pip install -r requirements.txt
```
This step ensures modules like `pandas` are available before running `orchestrator.py`.

> **Note**
> 
> This simplified version uses **Python 3.11 only** and includes:
> - **TPOT** (genetic programming AutoML)
> - **AutoGluon** (ensemble AutoML)
> - **XGBoost, LightGBM** (gradient boosting)
> 
> Auto-Sklearn support has been removed to eliminate Python version compatibility issues.

## Git Repository Structure

This repository has three main branches:
- **`main`** - Primary development branch
- **`master`** - Mirror of main branch  
- **`V1.1`** - Version 1.1 feature branch

## Python Environment Management

This project now uses a **single Python 3.11 environment** to simplify setup:

- **`env-tpa`** - TPOT + AutoGluon environment (Python 3.11)

### Quick Environment Usage

```bash
# Activate the AutoML environment
./activate.sh

# Deactivate the environment
deactivate
```

### Python Requirements

- **Python 3.11** (required)
- Build tools (`build-essential` on Ubuntu, `base-devel` on Arch)

For installation on different systems:
```bash
# Ubuntu/Debian  
sudo apt install python3.11 python3.11-venv python3.11-dev

# Arch Linux (use AUR)
yay -S python311
```

### Manual Installation (if setup.sh fails)

```bash
# Create environment
python3.11 -m venv env-tpa

# Install dependencies
source env-tpa/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
```

## Running the Orchestrator

```bash
# Activate the environment
./activate.sh

# Run both engines (TPOT + AutoGluon)
python orchestrator.py --all --time 3600 \
  --data DataSets/3/predictors_Hold\ 1\ Full_20250527_151252.csv \
  --target DataSets/3/targets_Hold\ 1\ Full_20250527_151252.csv

# Run only AutoGluon
python orchestrator.py --autogluon --time 1800 \
  --data DataSets/3/predictors.csv \
  --target DataSets/3/targets.csv

# Run only TPOT
python orchestrator.py --tpot --time 1800 \
  --data DataSets/3/predictors.csv \
  --target DataSets/3/targets.csv

deactivate
```

All orchestrations run **AutoGluon** and **TPOT** engines. The `--all` flag ensures every run evaluates both engines before selecting a champion.

## Project Structure

```
AutoML-Harness/
├── orchestrator.py              # Main entry point
├── setup.sh                     # One-command setup script
├── activate.sh                  # Environment activation
├── engines/                     # AutoML engine wrappers
├── components/                  # Preprocessors and models
├── DataSets/                    # Input datasets
├── 05_outputs/                  # Generated artifacts and results
└── requirements.txt             # Dependencies (Python 3.11)
```

## Output Artifacts

All runs generate artifacts in `05_outputs/<dataset_name>/`:
- **`*_champion.pkl`** - Trained pipeline for each engine
- **`metrics.json`** - Comprehensive 5×3 CV performance metrics  
- **`*.log`** - Detailed execution logs

## System Requirements

- Linux (recommended) or macOS
- **Python 3.11** (required)
- 8GB+ RAM for larger datasets
- Build tools (`build-essential` on Ubuntu, `base-devel` on Arch) 

## Supported AutoML Engines

| Engine | Description | Strengths |
|--------|-------------|-----------|
| **AutoGluon** | Ensemble methods + neural architecture search | Fast, often wins competitions |
| **TPOT** | Genetic programming evolution | Finds novel pipeline combinations |

## Troubleshooting

- **Environment not activated** – If you encounter `ModuleNotFoundError` or similar issues,
  activate the environment:

  ```bash
  ./activate.sh
  ```

  Deactivate the current environment at any time using `deactivate`.

- **Setup problems** – If `./setup.sh` fails, follow the instructions in the
  *Manual Installation* section to create the environment manually and
  install the required packages.

- **Python version issues** – This version requires Python 3.11. Check your version:
  ```bash
  python3.11 --version
  # or
  python3 --version  # should show 3.11.x
  ```

## License

This project is licensed under the [MIT License](LICENSE).

