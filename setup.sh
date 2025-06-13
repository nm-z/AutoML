#!/bin/bash

# AutoML Harness Setup Script
# This script sets up the AutoML environment with Python 3.11 only
# Auto-Sklearn support has been removed to simplify dependency management

set -e  # Exit on any error

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
    
    # Check for Python 3.11 (required)
    if command -v python3.11 &> /dev/null; then
        PYTHON_CMD="python3.11"
        log_success "Found Python 3.11 (required)"
    elif command -v python3 &> /dev/null; then
        # Check if python3 is actually 3.11
        PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        if [[ "$PYTHON_VERSION" == "3.11" ]]; then
            PYTHON_CMD="python3"
            log_success "Found Python 3.11 as default python3"
        else
            log_error "Python 3.11 is required but not found. Current python3 version: $PYTHON_VERSION"
            log_info "For Ubuntu/Debian: sudo apt install python3.11 python3.11-venv python3.11-dev"
            log_info "For Arch: Use AUR package python311 or compile from source"
            exit 1
        fi
    else
        log_error "Python 3.11 is required but not found. Please install Python 3.11 before running this setup script."
        log_info "For Ubuntu/Debian: sudo apt install python3.11 python3.11-venv python3.11-dev"
        log_info "For Arch: Use AUR package python311 or compile from source"
        exit 1
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

# Create virtual environment (only env-tpa needed now)
create_environment() {
    log_info "Creating Python virtual environment..."

    # Remove existing environment if it exists
    if [ -d "env-tpa" ]; then
        log_info "Removing existing env-tpa environment..."
        rm -rf env-tpa
    fi
    
    log_info "Creating env-tpa (TPOT + AutoGluon environment)..."
    $PYTHON_CMD -m venv env-tpa
    log_success "Created env-tpa environment"
}

# Install dependencies
install_dependencies() {
    log_info "Installing dependencies..."

    source env-tpa/bin/activate

    # Upgrade pip first
    pip install --upgrade pip

    # Install core dependencies without Auto-Sklearn
    log_info "Installing TPOT + AutoGluon dependencies..."
    pip install --only-binary=:all: \
        numpy==1.26.4 \
        rich==13.7.0 \
        pandas==2.2.1 \
        joblib==1.3.2 \
        scikit-learn==1.4.2 \
        tpot==0.12.2 \
        scipy==1.11.4 \
        "autogluon.tabular[all]==1.3.1" \
        psutil==5.9.8 \
        xgboost==2.0.3 \
        lightgbm==4.3.0 \
        python-logstash-async==2.9.0 \
        matplotlib \
        seaborn

    deactivate
    log_success "Dependencies installed successfully"
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

# Test environment
test_environment() {
    log_info "Testing environment installation..."
    
    source env-tpa/bin/activate
    
    python -c "
import tpot
import autogluon.tabular as ag
import xgboost as xgb
import lightgbm as lgb
import sklearn
import numpy as np
import pandas as pd
print('✓ AutoML environment working correctly')
print(f'  - TPOT version: {tpot.__version__}')
print(f'  - AutoGluon version: {ag.__version__}')
print(f'  - XGBoost version: {xgb.__version__}')
print(f'  - LightGBM version: {lgb.__version__}')
print(f'  - Scikit-learn version: {sklearn.__version__}')
print(f'  - NumPy version: {np.__version__}')
print(f'  - Pandas version: {pd.__version__}')
"
    
    deactivate
    log_success "Environment test passed"
}

# Create activation script
create_activation_script() {
    log_info "Creating activation script..."
    
    cat > activate.sh << 'EOF'
#!/bin/bash
# AutoML Environment Activation Script
source env-tpa/bin/activate
echo "✓ AutoML environment activated (TPOT + AutoGluon + Python 3.11)"
echo "To deactivate, run: deactivate"
EOF
    
    chmod +x activate.sh
    log_success "Created activate.sh script"
}

# Cleanup old files
cleanup_old_files() {
    log_info "Cleaning up old Auto-Sklearn files..."
    
    # Remove Auto-Sklearn activation script
    if [ -f "activate-as.sh" ]; then
        rm activate-as.sh
        log_info "Removed activate-as.sh"
    fi
    
    # Remove env-as directory if it exists
    if [ -d "env-as" ]; then
        rm -rf env-as
        log_info "Removed env-as directory"
    fi
    
    log_success "Cleanup completed"
}

# Main execution
main() {
    echo "=========================================="
    echo "       AutoML Harness Setup Script       "
    echo "     Python 3.11 Only (Simplified)      "
    echo "=========================================="
    echo
    
    check_system
    install_system_deps
    create_environment
    install_dependencies
    create_directories
    test_environment
    create_activation_script
    cleanup_old_files
    
    echo
    log_success "Setup completed successfully!"
    echo
    echo "To activate the environment, run:"
    echo "  ./activate.sh"
    echo
    echo "Then you can run the orchestrator:"
    echo "  python orchestrator.py --help"
    echo
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            echo "AutoML Harness Setup Script (Python 3.11 Only)"
            echo
            echo "Usage: $0 [options]"
            echo
            echo "This script sets up a single Python 3.11 environment with:"
            echo "  - TPOT (genetic programming AutoML)"
            echo "  - AutoGluon (ensemble AutoML)"
            echo "  - XGBoost, LightGBM"
            echo "  - All required dependencies"
            echo
            echo "Auto-Sklearn support has been removed to simplify setup."
            echo
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
    shift
done

# Run main function
main 