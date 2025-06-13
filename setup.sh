#!/bin/bash

# AutoML Harness Setup Script
# This script sets up the complete AutoML environment with proper Python environments

set -e  # Exit on any error

# Optional Auto-Sklearn environment
ENABLE_AS=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Linux
check_system() {
    log_info "Checking system compatibility..."
    if [[ "$OSTYPE" != "linux-gnu"* ]]; then
        log_warning "This script is optimized for Linux. Continuing anyway..."
    fi
    
    # Check for available Python versions (prefer 3.10, fallback to 3.9)
    if command -v python3.10 &> /dev/null; then
        PYTHON_CMD="python3.10"
        log_success "Found Python 3.10 (required)"
    elif command -v python3.9 &> /dev/null; then
        PYTHON_CMD="python3.9"
        log_success "Found Python 3.9 (required)"
    else
        log_error "Python 3.10 or 3.9 is required but neither was found. Please install Python 3.10 or 3.9 before running this setup script."
        log_info "For Ubuntu/Debian: sudo apt install python3.10 python3.10-venv python3.10-dev"
        log_info "For Arch: sudo pacman -S python310"
        exit 1
    fi
    
    PYTHON_MINOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.minor)')
    if [ "$PYTHON_MINOR" -le 10 ]; then
        ENABLE_AS=true
    fi
    log_success "System check passed - using $PYTHON_CMD"
}

# Install system dependencies
install_system_deps() {
    log_info "Checking system dependencies..."
    
    # Check if we can use package manager
    if command -v apt &> /dev/null; then
        log_info "Detected apt package manager"
        # We won't run sudo commands automatically, just inform user
        if ! dpkg -l | grep -q python3.10-dev; then
            log_warning "python3.10-dev not found. You may need to run:"
            log_warning "sudo apt update && sudo apt install -y python3.10-dev build-essential"
        fi
    elif command -v pacman &> /dev/null; then
        log_info "Detected pacman package manager"
        if ! pacman -Qi base-devel &> /dev/null; then
            log_warning "base-devel not found. You may need to run:"
            log_warning "sudo pacman -S base-devel"
        fi
    fi
}

# Setup pyenv if needed
setup_pyenv() {
    log_info "Checking pyenv installation..."
    
    if ! command -v pyenv &> /dev/null; then
        log_info "Installing pyenv..."
        curl https://pyenv.run | bash
        
        # Add pyenv to PATH for current session
        export PYENV_ROOT="$HOME/.pyenv"
        export PATH="$PYENV_ROOT/bin:$PATH"
        eval "$(pyenv init -)"
        eval "$(pyenv virtualenv-init -)"
        
        log_warning "Please add the following to your ~/.bashrc or ~/.zshrc:"
        echo 'export PYENV_ROOT="$HOME/.pyenv"'
        echo 'export PATH="$PYENV_ROOT/bin:$PATH"'
        echo 'eval "$(pyenv init -)"'
        echo 'eval "$(pyenv virtualenv-init -)"'
    else
        log_success "pyenv is already installed"
        # Ensure pyenv is initialized for the current shell session
        export PYENV_ROOT="$HOME/.pyenv"
        export PATH="$PYENV_ROOT/bin:$PATH"
        eval "$(pyenv init -)"
        eval "$(pyenv virtualenv-init -)"
    fi
}

# Create necessary directories
create_directories() {
    log_info "Creating required directories..."
    
    # Ensure all required directories exist per the workspace rules
    mkdir -p components/models
    mkdir -p components/preprocessors/scalers
    mkdir -p components/preprocessors/dimensionality  
    mkdir -p components/preprocessors/outliers
    mkdir -p engines
    mkdir -p 05_outputs
    mkdir -p DataSets/{1,2,3}
    
    log_success "Directory structure created"
}

# Setup pyenv environment and install dependencies
setup_pyenv_env() {
    log_info "Creating and setting up pyenv environment 'automl-harness'..."
    
    # Ensure Python 3.10 is available via pyenv
    if ! pyenv versions | grep -q "3.10"; then
        log_info "Installing Python 3.10 with pyenv..."
        pyenv install 3.10.13 || pyenv install 3.10
    fi
    
    # Create or recreate the pyenv virtual environment
    if pyenv virtualenvs | grep -q "automl-harness"; then
        log_info "Removing existing pyenv environment 'automl-harness'..."
        pyenv virtualenv-delete -f automl-harness
    fi
    log_info "Creating pyenv virtual environment 'automl-harness'..."
    pyenv virtualenv 3.10.13 automl-harness || pyenv virtualenv 3.10 automl-harness
    log_success "Created pyenv virtual environment 'automl-harness'"
    
    # Activate the environment and install dependencies
    pyenv activate automl-harness
    
    log_info "Upgrading pip..."
    pip install --upgrade pip
    
    log_info "Installing dependencies from requirements.txt..."
    pip install --only-binary=:all: -r requirements.txt
    
    log_info "Deactivating pyenv environment..."
    pyenv deactivate
    log_success "pyenv environment setup completed and dependencies installed"
}

# Test environment
test_environment() {
    log_info "Testing pyenv environment installation..."
    
    pyenv activate automl-harness
    
    python -c "
import tpot
import autogluon.tabular as ag
import sklearn
import numpy as np
import pandas as pd
print('✓ AutoML Harness environment working correctly')
print(f'  - TPOT version: {tpot.__version__}')
print(f'  - AutoGluon version: {ag.__version__}')
print(f'  - Scikit-learn version: {sklearn.__version__}')
print(f'  - NumPy version: {np.__version__}')
print(f'  - Pandas version: {pd.__version__}')
"
    pyenv deactivate
    
    log_success "Pyenv environment tested successfully"
}

# Post-setup check for all installed libraries
post_setup_check() {
    log_info "Running post-setup checks to verify library installations..."

    ALL_LIBS_OK=true

    pyenv activate automl-harness
    REQUIRED_LIBS=(
        "numpy"
        "pandas"
        "scikit-learn"
        "joblib"
        "rich"
        "tpot"
        "autogluon.tabular"
        "xgboost"
        "lightgbm"
    )
    for lib in "${REQUIRED_LIBS[@]}"; do
        log_info "Checking $lib..."
        if ! python -c "import $lib" &> /dev/null; then
            log_error "✗ $lib is NOT installed or cannot be imported."
            ALL_LIBS_OK=false
        else
            log_success "✓ $lib is installed."
        fi
    done
    pyenv deactivate

    if ! $ALL_LIBS_OK; then
        log_error "Post-setup check FAILED. Some required libraries are missing. Please review the errors above."
        exit 1
    else
        log_success "All required libraries verified successfully!"
    fi
}

# Main setup function
main() {
    echo "=========================================="
    echo "       AutoML Harness Setup Script       "
    echo "=========================================="
    echo ""

    for arg in "$@"; do
        if [ "$arg" = "--with-as" ]; then
            ENABLE_AS=true # This will be ignored in pyenv-only setup
        fi
    done
    
    check_system
    install_system_deps
    setup_pyenv
    create_directories
    setup_pyenv_env
    test_environment
    post_setup_check
    
    echo ""
    echo "=========================================="
    log_success "Setup completed successfully!"
    echo "=========================================="
    echo ""
    echo "Environment Usage:"
    echo "  • Activate: pyenv activate automl-harness"
    echo "  • Deactivate: pyenv deactivate"
    echo ""
    echo "Quick Start:"
    echo "  1. Activate: pyenv activate automl-harness"
    echo "  2. Run: python orchestrator.py --all --time 300 --data DataSets/3/predictors_Hold\\ 1\\ Full_20250527_151252.csv --target DataSets/3/targets_Hold\\ 1\\ Full_20250527_151252.csv"
    echo ""
    echo "For more information, see README.md"
    echo ""
}

# Run main function
main "$@" 