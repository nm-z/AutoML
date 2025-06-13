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
    
    # Check for available Python versions (strictly enforce 3.11)
    if command -v python3.11 &> /dev/null; then
        PYTHON_CMD="python3.11"
        log_success "Found Python 3.11 (required)"
    else
        log_error "Python 3.11 is required but not found. Please install Python 3.11 before running this setup script."
        log_info "For Ubuntu/Debian: sudo apt install python3.11 python3.11-venv python3.11-dev"
        log_info "For Arch: sudo pacman -S python311"
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
        if ! dpkg -l | grep -q python3.11-dev; then
            log_warning "python3.11-dev not found. You may need to run:"
            log_warning "sudo apt update && sudo apt install -y python3.11-dev build-essential"
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
    fi
}

# Create virtual environments
create_environments() {
    log_info "Creating Python virtual environments..."

    # env-tpa is always required
    if [ -d "env-tpa" ]; then
        log_info "Removing existing env-tpa environment..."
        rm -rf env-tpa
    fi
    log_info "Creating env-tpa (TPOT + AutoGluon environment)..."
    $PYTHON_CMD -m venv env-tpa
    log_success "Created env-tpa environment"

    # Create env-as only when requested
    if [ "$ENABLE_AS" = true ]; then
        if [ -d "env-as" ]; then
            log_info "Removing existing env-as environment..."
            rm -rf env-as
        fi
        log_info "Creating env-as (Auto-Sklearn environment)..."
        $PYTHON_CMD -m venv env-as
        log_success "Created env-as environment"
    else
        log_warning "Skipping env-as creation (requires Python <=3.10 or --with-as)"
    fi
}

# Install dependencies in env-tpa
install_env_tpa_deps() {
    log_info "Installing dependencies in env-tpa..."

    source env-tpa/bin/activate

    # Upgrade pip first
    pip install --upgrade pip

    # Install all Python dependencies from requirements.txt using wheels only
    if [[ "$PYTHON_CMD" == *"3.11"* ]]; then
        grep -v '^auto-sklearn' requirements.txt > /tmp/requirements_no_as.txt
        pip install --only-binary=:all: -r /tmp/requirements_no_as.txt
        rm /tmp/requirements_no_as.txt
    else
        pip install --only-binary=:all: -r requirements.txt
    fi

    deactivate
    log_success "env-tpa dependencies installed successfully"
}

# Install dependencies in env-as
install_env_as_deps() {
    if [ ! -d "env-as" ]; then
        log_warning "env-as environment not found. Skipping Auto-Sklearn dependencies"
        return
    fi

    log_info "Installing dependencies in env-as..."

    source env-as/bin/activate

    # Upgrade pip first
    pip install --upgrade pip

    if [[ "$PYTHON_CMD" == *"3.11"* ]]; then
        log_warning "Auto-Sklearn 0.15.0 is incompatible with Python 3.11; installing base stack only"
        pip install --only-binary=:all: numpy pandas scikit-learn==1.4.2 matplotlib seaborn rich joblib
    else
        pip install --only-binary=:all: auto-sklearn==0.15.0 numpy pandas scikit-learn==1.4.2 matplotlib seaborn rich joblib
    fi

    deactivate
    log_success "env-as dependencies installed successfully"
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

# Test environments
test_environments() {
    log_info "Testing environment installations..."
    
    # Test env-as only if it exists
    if [ -d "env-as" ]; then
        log_info "Testing env-as environment..."
        source env-as/bin/activate

        if [[ "$PYTHON_CMD" == "python3.13" ]]; then
            python -c "
import sklearn
import numpy as np
import pandas as pd
print('✓ Base scientific environment working correctly (Auto-sklearn skipped for Python 3.13)')
print(f'  - Scikit-learn version: {sklearn.__version__}')
print(f'  - NumPy version: {np.__version__}')
print(f'  - Pandas version: {pd.__version__}')
"
        else
            python -c "
import auto_sklearn.regression
import sklearn
import numpy as np
import pandas as pd
print('✓ Auto-Sklearn environment working correctly')
print(f'  - Auto-Sklearn version: {auto_sklearn.__version__}')
print(f'  - Scikit-learn version: {sklearn.__version__}')
print(f'  - NumPy version: {np.__version__}')
print(f'  - Pandas version: {pd.__version__}')
"
        fi
        deactivate
    else
        log_warning "env-as environment not found. Skipping Auto-Sklearn test."
    fi
    
    # Test env-tpa
    log_info "Testing env-tpa environment..."
    source env-tpa/bin/activate
    
    if [[ "$PYTHON_CMD" == "python3.13" ]]; then
        python -c "
import tpot
import sklearn
import numpy as np
import pandas as pd
print('✓ TPOT environment working correctly (AutoGluon skipped for Python 3.13)')
print(f'  - TPOT version: {tpot.__version__}')
print(f'  - Scikit-learn version: {sklearn.__version__}')
print(f'  - NumPy version: {np.__version__}')
print(f'  - Pandas version: {pd.__version__}')
try:
    import xgboost as xgb
    print(f'  - XGBoost version: {xgb.__version__}')
except ImportError:
    print('  - XGBoost: Not available')
try:
    import lightgbm as lgb
    print(f'  - LightGBM version: {lgb.__version__}')
except ImportError:
    print('  - LightGBM: Not available')
"
    else
        python -c "
import tpot
import autogluon.tabular as ag
import sklearn
import numpy as np
import pandas as pd
print('✓ TPOT + AutoGluon environment working correctly')
print(f'  - TPOT version: {tpot.__version__}')
print(f'  - AutoGluon version: {ag.__version__}')
print(f'  - Scikit-learn version: {sklearn.__version__}')
print(f'  - NumPy version: {np.__version__}')
print(f'  - Pandas version: {pd.__version__}')
"
    fi
    deactivate
    
    log_success "All environments tested successfully"
}

# Post-setup check for all installed libraries
post_setup_check() {
    log_info "Running post-setup checks to verify library installations..."

    ALL_LIBS_OK=true

    # Check env-tpa libraries
    source env-tpa/bin/activate
    REQUIRED_TPA_LIBS=(
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
    for lib in "${REQUIRED_TPA_LIBS[@]}"; do
        log_info "Checking $lib..."
        if ! python -c "import $lib" &> /dev/null; then
            log_error "✗ $lib is NOT installed or cannot be imported."
            ALL_LIBS_OK=false
        else
            log_success "✓ $lib is installed."
        fi
    done
    deactivate

    # Check env-as libraries if env-as exists
    if [ -d "env-as" ]; then
        source env-as/bin/activate
        REQUIRED_AS_LIBS=(
            "numpy"
            "pandas"
            "scikit-learn"
            "joblib"
            "rich"
            "auto_sklearn.regression"
        )
        for lib in "${REQUIRED_AS_LIBS[@]}"; do
            log_info "Checking $lib..."
            if ! python -c "import $lib" &> /dev/null; then
                log_error "✗ $lib is NOT installed or cannot be imported."
                ALL_LIBS_OK=false
            else
                log_success "✓ $lib is installed."
            fi
        done
        deactivate
    else
        log_warning "env-as environment not found. Skipping Auto-Sklearn library checks."
    fi

    if ! $ALL_LIBS_OK; then
        log_error "Post-setup check FAILED. Some required libraries are missing. Please review the errors above."
        exit 1
    else
        log_success "All required libraries verified successfully!"
    fi
}

# Create environment activation scripts
create_activation_scripts() {
    log_info "Creating environment activation scripts..."

    # Create activate-as.sh
    cat > activate-as.sh << 'EOF'
#!/bin/bash
# Activate Auto-Sklearn environment
echo "Activating Auto-Sklearn environment (env-as)..."
source env-as/bin/activate
echo "✓ Auto-Sklearn environment activated"
echo "Use 'deactivate' to exit the environment"
EOF
    chmod +x activate-as.sh

    # Create activate-tpa.sh
    cat > activate-tpa.sh << 'EOF'
#!/bin/bash
# Activate TPOT + AutoGluon environment
echo "Activating TPOT + AutoGluon environment (env-tpa)..."
source env-tpa/bin/activate
echo "✓ TPOT + AutoGluon environment activated"
echo "Use 'deactivate' to exit the environment"
EOF
    chmod +x activate-tpa.sh

    log_success "Activation scripts created"
}

# Main setup function
main() {
    echo "=========================================="
    echo "       AutoML Harness Setup Script       "
    echo "=========================================="
    echo ""

    for arg in "$@"; do
        if [ "$arg" = "--with-as" ]; then
            ENABLE_AS=true
        fi
    done
    
    check_system
    install_system_deps
    # setup_pyenv  # Commented out to use system Python directly
    create_directories
    create_environments
    if [ "$ENABLE_AS" = true ]; then
        install_env_as_deps
    fi
    install_env_tpa_deps
    test_environments
    post_setup_check
    create_activation_scripts
    
    echo ""
    echo "=========================================="
    log_success "Setup completed successfully!"
    echo "=========================================="
    echo ""
    echo "Environment Usage:"
    echo "  • TPOT + AutoGluon: ./activate-tpa.sh"
    echo "  • Auto-Sklearn:     ./activate-as.sh (optional)"
    echo ""
    echo "Quick Start:"
    echo "  1. Run: ./activate-tpa.sh"
    echo "  2. Test: python orchestrator.py --all --time 300 --data DataSets/3/predictors_Hold\\ 1\\ Full_20250527_151252.csv --target DataSets/3/targets_Hold\\ 1\\ Full_20250527_151252.csv"
    echo "  3. Optionally try Auto-Sklearn with ./activate-as.sh"
    echo ""
    echo "For more information, see README.md"
    echo ""
}

# Run main function
main "$@" 